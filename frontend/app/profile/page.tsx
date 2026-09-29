"use client";
import {FormEvent,useEffect,useState} from "react";
import {useRouter} from "next/navigation";
import Nav from "@/components/Nav";
import {api,Profile,requireAuth} from "@/lib/api";

const empty:Profile={degree_level:null,university:null,major:null,academic_year:null,nationality:null,gpa:null,gpa_scale:4,languages:{},skills:[],interests:[],preferred_opportunity_types:[],preferred_locations:[],remote_preference:null,extra_data:{}};
const csv=(value:string)=>value.split(",").map(x=>x.trim()).filter(Boolean);
const languageText=(value:Record<string,string>)=>Object.entries(value).map(([name,level])=>`${name}: ${level}`).join(", ");

export default function ProfilePage(){
  const router=useRouter(); const [profile,setProfile]=useState<Profile>(empty); const [message,setMessage]=useState("");
  useEffect(()=>{requireAuth(router);api<Profile>("/api/profile").then(setProfile).catch(()=>{})},[router]);
  async function submit(event:FormEvent<HTMLFormElement>){
    event.preventDefault(); const data=new FormData(event.currentTarget);
    const languages=Object.fromEntries(csv(String(data.get("languages")||"")).map(pair=>{const [name,...rest]=pair.split(":");return [name.trim(),rest.join(":").trim()]}).filter(x=>x[0]&&x[1]));
    const body={...profile,degree_level:data.get("degree_level")||null,university:data.get("university")||null,major:data.get("major")||null,academic_year:data.get("academic_year")||null,nationality:data.get("nationality")||null,gpa:data.get("gpa")?Number(data.get("gpa")):null,gpa_scale:data.get("gpa_scale")?Number(data.get("gpa_scale")):null,languages,skills:csv(String(data.get("skills")||"")),interests:csv(String(data.get("interests")||"")),preferred_opportunity_types:csv(String(data.get("types")||"")),preferred_locations:csv(String(data.get("locations")||"")),remote_preference:data.get("remote")==="either"?null:data.get("remote")==="yes"};
    try{setProfile(await api<Profile>("/api/profile",{method:"PUT",body:JSON.stringify(body)}));setMessage("Profile saved. Your recommendations are ready.")}catch(error){setMessage(error instanceof Error?error.message:"Could not save")}
  }
  return <><Nav/><main className="page narrow"><div className="pageTitle"><span className="eyebrow">Your matching profile</span><h1>Tell us what fits.</h1><p>Unknown requirements stay uncertain—they never silently count against you.</p></div>
    <form key={profile.id||"new"} className="profileForm" onSubmit={submit}>
      <div className="grid">
        <label>Degree level<input name="degree_level" defaultValue={profile.degree_level||""} placeholder="Bachelor's"/></label>
        <label>University<input name="university" defaultValue={profile.university||""}/></label>
        <label>Major<input name="major" defaultValue={profile.major||""} placeholder="Computer Science"/></label>
        <label>Academic year<input name="academic_year" defaultValue={profile.academic_year||""} placeholder="Third year"/></label>
        <label>Nationality<input name="nationality" defaultValue={profile.nationality||""}/></label>
        <label>GPA<input name="gpa" type="number" step="0.01" min="0" defaultValue={profile.gpa??""}/></label>
        <label>GPA scale<input name="gpa_scale" type="number" step="0.1" min="0.1" defaultValue={profile.gpa_scale??4}/></label>
        <label>Remote preference<select name="remote" defaultValue={profile.remote_preference===null?"either":profile.remote_preference?"yes":"no"}><option value="either">Either</option><option value="yes">Prefer remote</option><option value="no">Prefer on-site</option></select></label>
      </div>
      <label>Languages <small>comma-separated Language: Level</small><input name="languages" defaultValue={languageText(profile.languages)} placeholder="English: Professional Fluency, Korean: Basic"/></label>
      <label>Skills <small>comma-separated</small><input name="skills" defaultValue={profile.skills.join(", ")} placeholder="Python, ROS2, Computer Vision"/></label>
      <label>Interests and research interests<input name="interests" defaultValue={profile.interests.join(", ")} placeholder="Robotics, AI, climate policy"/></label>
      <label>Preferred opportunity types<input name="types" defaultValue={profile.preferred_opportunity_types.join(", ")} placeholder="Internship, Fellowship, Scholarship"/></label>
      <label>Preferred locations<input name="locations" defaultValue={profile.preferred_locations.join(", ")} placeholder="Germany, Seoul, Remote"/></label>
      {message&&<p className={message.includes("saved")?"success":"error"}>{message}</p>}
      <div className="actions"><button>Save profile</button><button type="button" className="secondary" onClick={()=>router.push("/feed")}>View recommendations</button></div>
    </form></main></>
}
