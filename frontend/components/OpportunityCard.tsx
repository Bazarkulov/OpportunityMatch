"use client";
import Link from "next/link";
import { api, Recommendation } from "@/lib/api";
import { useState } from "react";
export default function OpportunityCard({item,onSavedChange}:{item:Recommendation;onSavedChange?:(saved:boolean)=>void}){
  const [saved,setSaved]=useState(item.opportunity.saved);
  const [busy,setBusy]=useState(false);
  const [error,setError]=useState("");
  const o=item.opportunity;
  async function toggle(){
    setBusy(true);
    setError("");
    try{
      const nextSaved=!saved;
      await api(`/api/saved/${o.id}`,{method:saved?"DELETE":"POST"});
      setSaved(nextSaved);
      onSavedChange?.(nextSaved);
    }catch(err){
      setError(err instanceof Error?err.message:"Could not update saved status.");
    }finally{
      setBusy(false);
    }
  }
  return <article className="card">
    <div className="cardTop">
      <span className="eyebrow">{o.opportunity_type||"Opportunity"}</span>
      <span className={`status ${item.eligibility.status}`}>{item.eligibility.status}</span>
    </div>
    {saved&&<span className="savedBadge">Saved</span>}
    <h2><Link href={`/opportunities/${o.id}`}>{o.title}</Link></h2>
    <p className="organization">{o.organization}</p>
    <div className="meta">
      <span>{o.location||"Location not published"}</span>
      <span>{o.deadline?`Deadline ${o.deadline}`:"Deadline not published"}</span>
    </div>
    <div className="score"><strong>{Math.round(item.match.overall_score)}%</strong><span>match</span></div>
    <p>{item.match.matched_characteristics.length?`Strong matches: ${item.match.matched_characteristics.slice(0,3).join(", ")}`:"Recommendation based on your overall profile."}</p>
    <details className="matchDetails">
      <summary>Why this match?</summary>
      <p className="explanationIntro">{item.match.explanation}</p>
      {item.match.components.map((component)=>(
        <div className="component" key={component.name}>
          <div><span>{component.name.replaceAll("_"," ")}</span><b>{Math.round(component.score)}%</b></div>
          <div className="bar"><i style={{width:`${component.score}%`}}/></div>
          <small>{component.explanation} Weight: {Math.round(component.weight*100)}%.</small>
        </div>
      ))}
      {item.match.matched_characteristics.length>0&&<p><strong>Matched:</strong> {item.match.matched_characteristics.join(", ")}</p>}
      {item.match.missing_preferred_characteristics.length>0&&<p><strong>Preferred skills not listed in your profile:</strong> {item.match.missing_preferred_characteristics.join(", ")}</p>}
      <h3>Eligibility: <span className={`status ${item.eligibility.status}`}>{item.eligibility.status}</span></h3>
      {item.eligibility.passed.map((reason)=><p className="check" key={reason}>✓ {reason}</p>)}
      {item.eligibility.failed.map((reason)=><p className="failedLine" key={reason}>× {reason}</p>)}
      {item.eligibility.unknown.map((reason)=><p className="unknownLine" key={reason}>? {reason}</p>)}
    </details>
    {error&&<p className="error" role="alert">{error}</p>}
    <div className="actions">
      <Link className="button secondary" href={`/opportunities/${o.id}`}>View details</Link>
      <button disabled={busy} onClick={toggle}>{busy?"Saving…":saved?"Saved ✓":"Save"}</button>
    </div>
  </article>
}
