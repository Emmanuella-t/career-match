import Link from "next/link";

const links = [
  { href: "/", label: "Overview" },
  { href: "/match", label: "Prototype" },
  { href: "/architecture", label: "Architecture" },
];

export function SiteHeader() {
  return (
    <header className="border-b bg-background/90 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between sm:px-6">
        <Link href="/" className="font-semibold tracking-tight">
          Career Match
        </Link>
        <nav className="flex flex-wrap gap-x-4 gap-y-2 text-sm text-muted-foreground">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="hover:text-foreground"
            >
              {link.label}
            </Link>
          ))}
        </nav>
      </div>
    </header>
  );
}
