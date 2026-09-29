"use client";
import Link from "next/link";
import { useRouter } from "next/navigation";
export default function Nav(){ const router=useRouter(); return <header><Link className="brand" href="/feed">OpportunityMatch</Link><nav><Link href="/feed">Discover</Link><Link href="/saved">Saved</Link><Link href="/profile">Profile</Link><button className="linkButton" onClick={()=>{localStorage.removeItem("token");router.push("/login")}}>Log out</button></nav></header> }
