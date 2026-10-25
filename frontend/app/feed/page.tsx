"use client";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import Nav from "@/components/Nav";
import OpportunityCard from "@/components/OpportunityCard";
import { api, Recommendation, requireAuth } from "@/lib/api";
type SortOrder = "relevance" | "newest" | "deadline";

export default function Feed() {
  const router = useRouter();
  const [items, setItems] = useState<Recommendation[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [skill, setSkill] = useState("");
  const [location, setLocation] = useState("");
  const [type, setType] = useState("");
  const [deadlineWindow, setDeadlineWindow] = useState("");
  const [status, setStatus] = useState("");
  const [sort, setSort] = useState<SortOrder>("relevance");

  useEffect(() => {
    requireAuth(router);
    api<Recommendation[]>("/api/recommendations")
      .then(setItems)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [router]);

  const types = useMemo(
    () => Array.from(new Set(items.map(({ opportunity }) => opportunity.opportunity_type).filter((value): value is string => Boolean(value)))).sort(),
    [items],
  );

  const filteredItems = useMemo(() => {
    const now = new Date();
    const normalizedSearch = search.trim().toLocaleLowerCase();
    const normalizedSkill = skill.trim().toLocaleLowerCase();
    const normalizedLocation = location.trim().toLocaleLowerCase();
    return items
      .filter(({ opportunity: item, eligibility }) => {
        const searchable = `${item.title} ${item.organization}`.toLocaleLowerCase();
        const itemSkills = [...(item.required_skills ?? []), ...(item.preferred_skills ?? []), ...(item.keywords ?? [])]
          .map((value) => value.toLocaleLowerCase());
        const deadlineDays = item.deadline
          ? (new Date(`${item.deadline}T00:00:00`).getTime() - new Date(now.toDateString()).getTime()) / 86_400_000
          : null;
        return (
          (!normalizedSearch || searchable.includes(normalizedSearch)) &&
          (!normalizedSkill || itemSkills.some((value) => value.includes(normalizedSkill))) &&
          (!normalizedLocation || (item.location ?? "").toLocaleLowerCase().includes(normalizedLocation)) &&
          (!type || item.opportunity_type === type) &&
          (!deadlineWindow ||
            (deadlineWindow === "none" ? deadlineDays === null : deadlineDays !== null && deadlineDays >= 0 && deadlineDays <= Number(deadlineWindow))) &&
          (!status ||
            (status === "saved" ? item.saved : status === "eligible" ? eligibility.status === "eligible" : eligibility.status === "uncertain"))
        );
      })
      .sort((a, b) => {
        if (sort === "newest") {
          const dateA = new Date(a.opportunity.published_at ?? a.opportunity.discovered_at).getTime();
          const dateB = new Date(b.opportunity.published_at ?? b.opportunity.discovered_at).getTime();
          return dateB - dateA;
        }
        if (sort === "deadline") {
          const deadlineA = a.opportunity.deadline ? new Date(`${a.opportunity.deadline}T00:00:00`).getTime() : Number.MAX_SAFE_INTEGER;
          const deadlineB = b.opportunity.deadline ? new Date(`${b.opportunity.deadline}T00:00:00`).getTime() : Number.MAX_SAFE_INTEGER;
          return deadlineA - deadlineB;
        }
        return b.match.overall_score - a.match.overall_score;
      });
  }, [items, search, skill, location, type, deadlineWindow, status, sort]);

  function updateSaved(id: string, saved: boolean) {
    setItems((current) => current.map((item) =>
      item.opportunity.id === id ? { ...item, opportunity: { ...item.opportunity, saved } } : item,
    ));
  }

  function clearFilters() {
    setSearch("");
    setSkill("");
    setLocation("");
    setType("");
    setDeadlineWindow("");
    setStatus("");
    setSort("relevance");
  }

  return (
    <>
      <Nav />
      <main className="page">
        <div className="pageTitle">
          <span className="eyebrow">Personalized discovery</span>
          <h1>Opportunities worth your attention.</h1>
          <p>Ranked from real public listings. Uncertain eligibility is shown—not hidden.</p>
        </div>

        {!loading && !error && items.length > 0 && (
          <section className="feedFilters" aria-label="Filter and sort opportunities">
            <div className="filterGrid">
              <label>Search
                <input value={search} onChange={(event) => setSearch(event.target.value)} placeholder="Title or organization" />
              </label>
              <label>Skill
                <input value={skill} onChange={(event) => setSkill(event.target.value)} placeholder="e.g. Python" />
              </label>
              <label>Location
                <input value={location} onChange={(event) => setLocation(event.target.value)} placeholder="e.g. Remote, Boston" />
              </label>
              <label>Opportunity type
                <select value={type} onChange={(event) => setType(event.target.value)}>
                  <option value="">All types</option>
                  {types.map((value) => <option key={value} value={value}>{value}</option>)}
                </select>
              </label>
              <label>Deadline
                <select value={deadlineWindow} onChange={(event) => setDeadlineWindow(event.target.value)}>
                  <option value="">Any deadline</option>
                  <option value="7">Within 7 days</option>
                  <option value="30">Within 30 days</option>
                  <option value="none">No published deadline</option>
                </select>
              </label>
              <label>Status
                <select value={status} onChange={(event) => setStatus(event.target.value)}>
                  <option value="">All statuses</option>
                  <option value="saved">Saved</option>
                  <option value="eligible">Eligible</option>
                  <option value="uncertain">Eligibility uncertain</option>
                </select>
              </label>
              <label>Sort by
                <select value={sort} onChange={(event) => setSort(event.target.value as SortOrder)}>
                  <option value="relevance">Relevance</option>
                  <option value="newest">Newest</option>
                  <option value="deadline">Deadline</option>
                </select>
              </label>
            </div>
            <div className="filterSummary">
              <span>{filteredItems.length} of {items.length} opportunities</span>
              <button className="linkButton" type="button" onClick={clearFilters}>Clear filters</button>
            </div>
          </section>
        )}

        {loading && <p>Building your feed…</p>}
        {error && <div className="empty"><h2>Complete your matching profile</h2><p>{error}</p><button onClick={() => router.push("/profile")}>Set up profile</button></div>}
        {!loading && !error && items.length === 0 && <div className="empty"><h2>No current matches yet</h2><p>Refresh the opportunity collection, or broaden your profile preferences.</p></div>}
        {!loading && !error && items.length > 0 && filteredItems.length === 0 && <div className="empty filterEmpty"><h2>No opportunities match these filters</h2><p>Try removing a filter to see more recommendations.</p><button className="secondary" onClick={clearFilters}>Clear filters</button></div>}
        <section className="cards">
          {filteredItems.map((item) => <OpportunityCard key={item.opportunity.id} item={item} onSavedChange={(saved) => updateSaved(item.opportunity.id, saved)} />)}
        </section>
      </main>
    </>
  );
}
