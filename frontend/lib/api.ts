export const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
export type Profile = {id?: string; user_id?: string; degree_level: string|null; university: string|null; major: string|null; academic_year: string|null; nationality: string|null; gpa: number|null; gpa_scale: number|null; languages: Record<string,string>; skills: string[]; interests: string[]; preferred_opportunity_types: string[]; preferred_locations: string[]; remote_preference: boolean|null; extra_data: Record<string,unknown>};
export type Opportunity = {id:string; title:string; organization:string; description:string; opportunity_type:string|null; source:string; source_url:string; location:string|null; remote:boolean|null; deadline:string|null; published_at:string|null; discovered_at:string; funding_status:string|null; degree_requirements:string[]|null; major_requirements:string[]|null; nationality_restrictions:string[]|null; minimum_gpa:number|null; language_requirements:Record<string,string>|null; required_skills:string[]|null; preferred_skills:string[]|null; fields:string[]|null; keywords:string[]|null; active:boolean; saved:boolean};
export type Recommendation = {opportunity: Opportunity; eligibility:{status:"eligible"|"ineligible"|"uncertain";passed:string[];failed:string[];unknown:string[]}; match:{overall_score:number;components:{name:string;score:number;weight:number;explanation:string}[];matched_characteristics:string[];missing_preferred_characteristics:string[];explanation:string}};
export function token() { return typeof window === "undefined" ? null : localStorage.getItem("token"); }
export async function api<T>(path:string, options:RequestInit = {}):Promise<T> {
  const auth = token(); const headers = new Headers(options.headers); headers.set("Content-Type", "application/json"); if(auth) headers.set("Authorization", `Bearer ${auth}`);
  const response = await fetch(`${API_URL}${path}`, {...options, headers, cache:"no-store"});
  if(!response.ok) { let detail = response.statusText; try { const body = await response.json(); detail = body.detail || detail; } catch {} throw new Error(detail); }
  return response.status === 204 ? undefined as T : response.json();
}
export function requireAuth(router:{replace:(path:string)=>void}) { if(!token()) router.replace("/login"); }
