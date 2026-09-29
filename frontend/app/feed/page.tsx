"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import Nav from "@/components/Nav";
import OpportunityCard from "@/components/OpportunityCard";
import { api, Recommendation, requireAuth } from "@/lib/api";
export default function Feed(){const router=useRouter();const [items,setItems]=useState<Recommendation[]>([]);const [error,setError]=useState("");const [loading,setLoading]=useState(true);useEffect(()=>{requireAuth(router);api<Recommendation[]>("/api/recommendations").then(setItems).catch(err=>setError(err.message)).finally(()=>setLoading(false))},[router]);return <><Nav/><main className="page"><div className="pageTitle"><span className="eyebrow">Personalized discovery</span><h1>Opportunities worth your attention.</h1><p>Ranked from real public listings. Uncertain eligibility is shown—not hidden.</p></div>{loading&&<p>Building your feed…</p>}{error&&<div className="empty"><h2>Complete your matching profile</h2><p>{error}</p><button onClick={()=>router.push("/profile")}>Set up profile</button></div>} {!loading&&!error&&!items.length&&<div className="empty"><h2>No current matches yet</h2><p>Refresh the opportunity collection, or broaden your profile preferences.</p></div>}<section className="cards">{items.map(item=><OpportunityCard key={item.opportunity.id} item={item}/>)}</section></main></>}
