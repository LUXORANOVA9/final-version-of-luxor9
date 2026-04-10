import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "LUXOR9 | Build Your AI Empire",
  description: "The Autonomous AI Company Operating System. Deploy 179 intelligent agents to manage 100 income streams. Built for solo founders and indie hackers.",
  keywords: ["AI agents", "autonomous AI", "AI company", "income streams", "multi-agent", "automation", "solo founder", "indie hacker"],
  authors: [{ name: "LUXOR9" }],
  openGraph: {
    title: "LUXOR9 | Build Your AI Empire",
    description: "Deploy 179 intelligent agents to manage 100 income streams automatically.",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "LUXOR9 | Build Your AI Empire",
    description: "Deploy 179 intelligent agents to manage 100 income streams automatically.",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-dark-bg antialiased">
        {children}
      </body>
    </html>
  );
}
