import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyD1cQDy2J_oVIyxDuCcH_6xXja3GZo9fVg",
  authDomain: "social-generator-7e569.firebaseapp.com",
  projectId: "social-generator-7e569",
  storageBucket: "social-generator-7e569.firebasestorage.app",
  messagingSenderId: "10421849996",
  appId: "1:10421849996:web:8d4c20ba3ed00f337d90a9",
  measurementId: "G-Z7JLHBSK8J"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
