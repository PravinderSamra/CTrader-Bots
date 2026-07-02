import { initializeApp, getApps } from 'firebase/app'
import { getAuth } from 'firebase/auth'
import { getFirestore } from 'firebase/firestore'

// VITE_FIREBASE_* are safe to ship in the client bundle by Firebase's own design — this
// config identifies which Firebase project to talk to, it grants nothing on its own.
// Protection comes entirely from Firestore Security Rules (see db/firestore.rules)
// plus requiring a real login (see LoginGate.tsx, no public sign-up). This is a
// different trust model to the bearer tokens described in README.md's "Security note"
// section, which must never be injected client-side.
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY ?? '',
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN ?? '',
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID ?? '',
  appId: import.meta.env.VITE_FIREBASE_APP_ID ?? '',
}

export const firebaseConfigured = Boolean(
  firebaseConfig.apiKey && firebaseConfig.authDomain && firebaseConfig.projectId && firebaseConfig.appId,
)

const app = getApps().length
  ? getApps()[0]
  : initializeApp(
      firebaseConfigured
        ? firebaseConfig
        : { apiKey: 'placeholder', authDomain: 'placeholder.firebaseapp.com', projectId: 'placeholder', appId: 'placeholder' },
    )

export const auth = getAuth(app)
export const db = getFirestore(app)
