import asyncio
import logging
from typing import List, Type, Callable, Dict, Any, TypeVar, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select, delete, func
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel
from datetime import datetime, timezone

from src.db.session import async_session, async_engine

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=SQLModel)
U = TypeVar("U", bound=SQLModel)

# Constants
DEFAULT_BATCH_SIZE = 100
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.5


async def push_integration_data(
    model_class: Type[T],
    records: List[Dict[str, Any]],
    batch_size: int = 100,
    strategy: str = "replace",
    create_table: bool = True,
) -> bool:
    """
    Push integration data to PostgreSQL.

    Args:
        model_class: The SQLModel class for the integration table
        records: List of dictionaries containing record data
        batch_size: Number of records to process in each batch
        strategy: 'replace' or 'append'
        create_table: Whether to create the table if it doesn't exist

    Returns:
        bool: True if successful, False otherwise
    """
    if not records:
        logger.warning(f"No records to push for {model_class.__name__}")
        return True

    try:
        # Ensure table exists if requested
        if create_table:
            # Use SQLModel metadata to create tables
            async with async_engine.begin() as conn:
                # Create only this specific table if it doesn't exist
                await conn.run_sync(
                    lambda sync_conn: SQLModel.metadata.create_all(
                        sync_conn, tables=[model_class.__table__]
                    )
                )
            logger.info(f"Ensured table {model_class.__tablename__} exists")

        logger.info(f"Pushing {len(records)} records to {model_class.__name__}")

        # Process in batches for better performance
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} ({len(batch)} records)")

            async with async_session() as session:
                try:
                    # Ensure all datetime fields are timezone-naive
                    for record in batch:
                        for key, value in list(record.items()):
                            if isinstance(value, datetime):
                                if value.tzinfo is not None:
                                    # Convert timezone-aware datetime to naive
                                    record[key] = value.replace(tzinfo=None)

                    # Create model instances
                    model_instances = [model_class(**record) for record in batch]

                    if strategy == "replace":
                        # For replace strategy, we need to handle duplicates
                        await handle_duplicates(session, model_class, model_instances)
                    else:  # append strategy
                        # Just add all records
                        session.add_all(model_instances)

                    await session.commit()
                    logger.info(f"Successfully committed batch {i//batch_size + 1}")

                except SQLAlchemyError as e:
                    logger.error(
                        f"Database error in batch {i//batch_size + 1}: {str(e)}"
                    )
                    await session.rollback()
                    raise

        return True

    except Exception as e:
        logger.error(f"Error pushing integration data: {str(e)}")
        import traceback

        logger.error(traceback.format_exc())
        return False


async def handle_duplicates(
    session: AsyncSession,
    model_class: Type[T],
    records: List[T],
    unique_fields: Optional[List[str]] = None,
) -> None:
    """
    Handle duplicate records based on unique fields.

    Args:
        session: SQLAlchemy session
        model_class: The SQLModel class
        records: List of model instances
        unique_fields: Fields to check for uniqueness (defaults to name and external_id if available)
    """
    # Default unique fields if not specified
    if not unique_fields:
        unique_fields = []
        # Check if model has common unique fields
        for field in ["name", "external_id", "api_id"]:
            if hasattr(model_class, field):
                unique_fields.append(field)

        # We'll skip season for now since it might not exist in the database yet
        # This avoids the error when the column doesn't exist

    if not unique_fields:
        # If no unique fields found, just add all records
        session.add_all(records)
        return

    for record in records:
        # Build query to find existing record
        query = select(model_class)
        for field in unique_fields:
            if hasattr(record, field) and getattr(record, field) is not None:
                query = query.where(
                    getattr(model_class, field) == getattr(record, field)
                )

        # Check if record exists
        try:
            result = await session.execute(query)
            existing = result.scalar_one_or_none()

            if existing:
                # Update existing record with new values
                for key, value in record.dict().items():
                    if key not in ["id"] and value is not None:
                        setattr(existing, key, value)
                session.add(existing)
            else:
                # Add new record
                session.add(record)
        except Exception as e:
            logger.error(f"Error handling duplicate for {record}: {str(e)}")
            # Add the record anyway
            session.add(record)


async def process_integration_data(
    source_model: Type[T],
    target_model: Type[U],
    processor_func: Callable[[T, AsyncSession], Optional[U]],
    condition: Any = None,
    batch_size: int = 100,
) -> Dict[str, int]:
    """
    Process data from integration tables to core models.

    Args:
        source_model: The source integration model class
        target_model: The target core model class
        processor_func: Function to process each record
        condition: Optional condition to filter records
        batch_size: Number of records to process in each batch

    Returns:
        Dict with statistics (created, updated, skipped, failed)
    """
    stats = {"created": 0, "updated": 0, "skipped": 0, "failed": 0}

    try:
        # Create a new async session
        async with async_session() as session:
            # Get unprocessed records
            query = select(source_model)

            # Add condition if provided
            if condition is not None:
                query = query.where(condition)
            else:
                # By default, only process unprocessed records if the model has a processed field
                if hasattr(source_model, "processed"):
                    query = query.where(not getattr(source_model, "processed"))

            result = await session.execute(query)
            records = result.scalars().all()

            if not records:
                logger.info(f"No {source_model.__name__} records to process")
                return stats

            logger.info(f"Processing {len(records)} {source_model.__name__} records")

            # Process in batches for better performance
            for i in range(0, len(records), batch_size):
                batch = records[i : i + batch_size]
                logger.info(
                    f"Processing batch {i//batch_size + 1} ({len(batch)} records)"
                )

                # Create a new async session for each batch to avoid session issues
                async with async_session() as batch_session:
                    # Fetch the same records in the new session to avoid detached instance errors
                    batch_ids = [record.id for record in batch]
                    batch_query = select(source_model).where(
                        source_model.id.in_(batch_ids)
                    )
                    batch_result = await batch_session.execute(batch_query)
                    batch_records = batch_result.scalars().all()

                    # Create a mapping of id to record for easy lookup
                    record_map = {record.id: record for record in batch_records}

                    for record_id in batch_ids:
                        try:
                            # Get the record from the mapping
                            record = record_map.get(record_id)
                            if not record:
                                logger.warning(
                                    f"Record with id {record_id} not found in batch session"
                                )
                                stats["failed"] += 1
                                continue

                            # Process the record and get the result
                            result = await processor_func(record, batch_session)

                            # Update stats based on processor result
                            if result is None:
                                stats["skipped"] += 1
                            elif (
                                hasattr(result, "id")
                                and getattr(result, "id") is not None
                            ):
                                # Check if this is a new or existing record
                                if getattr(result, "id") > 0:
                                    stats["updated"] += 1
                                else:
                                    stats["created"] += 1
                            else:
                                stats["created"] += 1

                        except Exception as e:
                            logger.error(f"Error processing record: {str(e)}")
                            stats["failed"] += 1
                            # Continue processing other records
                            continue

                    # Commit after each batch
                    try:
                        await batch_session.commit()
                        logger.info(f"Committed batch {i//batch_size + 1}")
                    except Exception as e:
                        logger.error(f"Error committing batch: {str(e)}")
                        await batch_session.rollback()

        return stats

    except Exception as e:
        logger.error(f"Error in process_integration_data: {str(e)}")
        return stats


async def retry_operation(
    operation: Callable[[], Any], max_retries: int = 3, backoff_factor: float = 1.5
) -> Any:
    """
    Retry an operation with exponential backoff.

    Args:
        operation: Async function to retry
        max_retries: Maximum number of retry attempts
        backoff_factor: Factor to increase wait time between retries

    Returns:
        Result of the operation
    """
    retries = 0
    last_exception = None

    while retries <= max_retries:
        try:
            if retries > 0:
                logger.info(f"Retry attempt {retries}/{max_retries}")

            return await operation()

        except Exception as e:
            last_exception = e
            retries += 1

            if retries <= max_retries:
                wait_time = backoff_factor**retries
                logger.warning(
                    f"Operation failed: {str(e)}. Retrying in {wait_time:.1f}s"
                )
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Operation failed after {max_retries} retries: {str(e)}")
                raise last_exception
