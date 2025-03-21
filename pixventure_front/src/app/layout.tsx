// app/layout.tsx

import "./globals.scss";
import "bootstrap/dist/css/bootstrap.min.css";
import "@fortawesome/fontawesome-svg-core/styles.css";
import Header from "../components/Header/Header";
import { ReactNode } from "react";
import { AuthProvider } from "../contexts/AuthContext";
import { NotificationProvider } from "@/contexts/NotificationContext";
import ElementMenuClientSetup from "./ElementMenuClientSetup";

export const metadata = {
  title: "My App with Global Menu",
  description: "Example of a global menu in Next.js 13+ using the App Router",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" data-bs-theme="dark">
      <head />

      <body>
        <AuthProvider>
          <NotificationProvider>
            <Header />
            <main className="container-fluid">
              <ElementMenuClientSetup>{children}</ElementMenuClientSetup>
            </main>
          </NotificationProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
