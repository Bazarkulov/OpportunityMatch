"use client";
import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";

export default function Login() {
  const router = useRouter();
  const [register, setRegister] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setBusy(true);
    setError("");

    const data = new FormData(e.currentTarget);

    try {
      const result = await api<{ access_token: string }>(`/api/auth/${register ? "register" : "login"}`, {
        method: "POST",
        body: JSON.stringify({
          email: data.get("email"),
          password: data.get("password"),
        }),
      });

      localStorage.setItem("token", result.access_token);
      router.push(register ? "/profile" : "/feed");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="authPage">
      <section className="hero">
        <span className="eyebrow">Your next step, made clearer</span>
        <h1>Find opportunities that fit who you are.</h1>
        <p>
          OpportunityMatch checks eligibility, explains uncertainty, and ranks real public listings around your profile.
        </p>

        <div className="featureList" aria-label="OpportunityMatch benefits">
          <div className="feature">
            <strong>Eligibility</strong>
            <span>See what qualifies and what remains uncertain.</span>
          </div>
          <div className="feature">
            <strong>Relevance</strong>
            <span>Weighted ranking based on skills, interests, and fit.</span>
          </div>
          <div className="feature">
            <strong>Clarity</strong>
            <span>Understand why a role is a match before you apply.</span>
          </div>
        </div>
      </section>

      <form className="authCard" onSubmit={submit}>
        <h2>{register ? "Create your account" : "Welcome back"}</h2>

        <label>
          Email
          <input name="email" type="email" required autoComplete="email" placeholder="you@example.com" />
        </label>

        <label>
          Password
          <input
            name="password"
            type="password"
            minLength={8}
            required
            autoComplete={register ? "new-password" : "current-password"}
            placeholder="Enter your password"
          />
        </label>

        {error && <p className="error">{error}</p>}

        <div className="actions">
          <button type="submit" disabled={busy}>
            {busy ? "Please wait…" : register ? "Register" : "Log in"}
          </button>
          <button
            className="secondary"
            type="button"
            onClick={() => setRegister(!register)}
          >
            {register ? "Already have an account? Log in" : "New here? Create an account"}
          </button>
        </div>
      </form>
    </main>
  );
}
