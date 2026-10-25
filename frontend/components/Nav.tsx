"use client";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";

export default function Nav() {
  const router = useRouter();
  const pathname = usePathname();

  function logout() {
    localStorage.removeItem("token");
    router.push("/login");
  }

  const navItems = [
    { href: "/feed", label: "Discover" },
    { href: "/saved", label: "Saved" },
    { href: "/profile", label: "Profile" },
  ];

  return (
    <header>
      <Link className="brand" href="/feed">OpportunityMatch</Link>
      <nav>
        {navItems.map(({ href, label }) => (
          <Link key={href} href={href} className={pathname === href ? "active" : ""}>
            {label}
          </Link>
        ))}
        <button className="linkButton" type="button" onClick={logout}>
          Log out
        </button>
      </nav>
    </header>
  );
}
