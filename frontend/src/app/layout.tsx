import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Geo-Political Simulator",
  description: "Turn-based geopolitical strategy simulation",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ja">
      <body>{children}</body>
    </html>
  );
}
