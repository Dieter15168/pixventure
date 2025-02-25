// app/layout.tsx

import "./globals.css"; // or your global CSS
import Header from "./Header";
import Menu from "./Menu";
import { ReactNode } from "react";

export const metadata = {
  title: "My App with Global Menu",
  description: "Example of a global menu in Next.js 13+ using the App Router",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head />
      <body>
        <Header />
        <Menu />
        <main style={{ margin: "1rem" }}>{children}</main>
      </body>
    </html>
  );
}
