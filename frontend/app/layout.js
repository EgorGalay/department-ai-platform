import "./globals.css";

export const metadata = {
  title: "Department AI Platform",
  description: "Локальная AI-платформа кафедры",
};

export default function RootLayout({ children }) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
