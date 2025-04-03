// app/layout.tsx

import "./globals.scss";
import "bootstrap/dist/css/bootstrap.min.css";
import "@fortawesome/fontawesome-free/css/all.min.css";
import "@fortawesome/fontawesome-svg-core/styles.css";
import Header from "../components/Header/Header";
import { ReactNode } from "react";
import { AuthProvider } from "../contexts/AuthContext";
import { NotificationProvider } from "@/contexts/NotificationContext";
import { ModalProvider } from "../contexts/ModalContext";
import ElementMenuClientSetup from "./ElementMenuClientSetup";
import GoogleTagManager from "@/components/GoogleTagManager";

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html
      lang="en"
      data-bs-theme="dark"
    >
      <head>
        <GoogleTagManager />
      </head>

      <body>
        <AuthProvider>
          <NotificationProvider>
            <Header />
            <main className="container-fluid">
              <ModalProvider>
                <ElementMenuClientSetup>{children}</ElementMenuClientSetup>
              </ModalProvider>
            </main>
          </NotificationProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
