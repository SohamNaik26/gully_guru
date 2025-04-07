# GullyGuru Frontend

This is the frontend application for GullyGuru Fantasy Cricket, built with Next.js, TypeScript, shadcn/ui, and NextAuth.js.

## Features

- User authentication with Google OAuth
- Dashboard for managing fantasy cricket leagues
- Create and join Gullies (fantasy leagues)
- Squad creation and management
- Auction interface for player bidding
- Live scoring and leaderboards
- Responsive design

## Prerequisites

- Node.js 16.14+
- npm or yarn
- Backend API running (see main repository README)

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/gullyguru.git
   cd gullyguru/frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   # or
   yarn install
   ```

3. Copy the environment variables:

   ```bash
   cp .env.local.example .env.local
   ```

4. Update the `.env.local` file with your Google OAuth credentials and other configuration.

5. Start the development server:

   ```bash
   npm run dev
   # or
   yarn dev
   ```

6. Open [http://localhost:3000](http://localhost:3000) in your browser.

## Environment Variables

The following environment variables are required:

- `NEXTAUTH_SECRET`: Secret used for signing Next-Auth.js tokens
- `NEXTAUTH_URL`: URL for Next-Auth.js callbacks (e.g., http://localhost:3000)
- `GOOGLE_CLIENT_ID`: Google OAuth Client ID
- `GOOGLE_CLIENT_SECRET`: Google OAuth Client Secret
- `NEXT_PUBLIC_API_URL`: URL of the backend API (e.g., http://localhost:8000)

### Generating NEXTAUTH_SECRET

You can use the provided script to generate a secure random string for your NEXTAUTH_SECRET:

```bash
node scripts/generate-secret.js
```

Copy the generated string to your `.env.local` file.

## Project Structure

```
src/
├── app/                # App router pages
│   ├── api/           # API routes
│   ├── auth/          # Authentication pages
│   ├── dashboard/     # Dashboard pages
│   └── ...
├── components/         # React components
│   ├── ui/            # shadcn/ui components
│   ├── layout/        # Layout components
│   └── ...
├── lib/                # Utility functions
│   ├── api-client.ts   # API client
│   ├── store.ts        # Global state (Zustand)
│   └── ...
└── hooks/              # Custom React hooks
```

## Authentication

This project uses NextAuth.js for authentication with Google OAuth. To set up Google OAuth:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Navigate to "APIs & Services" > "OAuth consent screen"
4. Configure the OAuth consent screen (External for personal use is fine)
5. Add any required scopes (email, profile)
6. Navigate to "APIs & Services" > "Credentials"
7. Create OAuth client ID credentials (Web application)
8. Add authorized JavaScript origins and redirect URIs
   - Origins: `http://localhost:3000`
   - Redirect URIs: `http://localhost:3000/api/auth/callback/google`
9. Copy the Client ID and Client Secret to your `.env.local` file

### Troubleshooting Authentication

If you encounter authentication issues:

1. Ensure your NEXTAUTH_SECRET is set in your .env.local file
2. Confirm your Google OAuth credentials are correct
3. Check that NEXTAUTH_URL is set to your application URL
4. Clear browser cookies and try signing in again
5. For session errors, restart the application after changing environment variables

## Contributing

Please read the [contribution guidelines](../CONTRIBUTING.md) before submitting a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.
