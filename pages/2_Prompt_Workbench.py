import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import streamlit as st

from modules.prompt_workbench.prompt_manager import (
    create_prompt, get_all_prompts, get_prompt,
    update_prompt, delete_prompt,
    save_run, rate_run, get_runs, get_all_runs,
    extract_variables, render_prompt,
)
from modules.prompt_workbench.prompt_tester import run_prompt, run_comparison, judge_outputs
from utils.helpers import get_groq_api_key
from database.db import init_db

init_db()

st.set_page_config(page_title="Prompt Workbench | QuantAI", page_icon="⚡", layout="wide")

st.title("Prompt Workbench")
st.caption("Build, test, refine, and version prompts for your team's AI use cases")

api_key = get_groq_api_key()

USE_CASES = [
    "Risk Summarization",
    "Market Commentary",
    "Regulatory Q&A",
    "Client Communication",
    "Trade Analysis",
    "Data Extraction",
    "Internal Enablement",
    "Other",
]

tab_library, tab_test, tab_compare, tab_history = st.tabs([
    "Prompt Library", "Test & Refine", "Compare Prompts", "Run History"
])


# ── TAB 1: Prompt Library ─────────────────────────────────────────────────────
with tab_library:
    col_list, col_form = st.columns([1, 1.6], gap="large")

    with col_list:
        st.subheader("Saved Prompts")
        prompts = get_all_prompts()

        if not prompts:
            st.info("No prompts yet. Create your first one →")
        else:
            for p in prompts:
                vars_detected = extract_variables(p["prompt_text"])
                var_badge = f" · `{len(vars_detected)} var(s)`" if vars_detected else ""
                with st.expander(f"**{p['name']}** — {p['use_case']}{var_badge}"):
                    st.markdown(f"```\n{p['prompt_text']}\n```")
                    if p["notes"]:
                        st.caption(f"Notes: {p['notes']}")
                    st.caption(f"Updated: {p['updated_at']}")

                    col_edit, col_del = st.columns(2)
                    with col_edit:
                        if st.button("Edit", key=f"edit_{p['id']}"):
                            st.session_state["edit_prompt"] = p
                    with col_del:
                        if st.button("Delete", key=f"del_{p['id']}"):
                            delete_prompt(p["id"])
                            st.success("Deleted.")
                            st.rerun()

    with col_form:
        editing = st.session_state.get("edit_prompt")
        st.subheader("Edit Prompt" if editing else "New Prompt")

        default_name = editing["name"] if editing else ""
        default_use_case = editing["use_case"] if editing else USE_CASES[0]
        default_text = editing["prompt_text"] if editing else ""
        default_notes = editing["notes"] if editing else ""

        name = st.text_input("Prompt name", value=default_name, placeholder="e.g. Risk Report Summarizer")
        use_case = st.selectbox(
            "Use case",
            USE_CASES,
            index=USE_CASES.index(default_use_case) if default_use_case in USE_CASES else 0,
        )
        prompt_text = st.text_area(
            "Prompt text",
            value=default_text,
            height=220,
            placeholder="Use {{variable}} for dynamic inputs.\ne.g. Summarize the following risk report:\n\n{{report_text}}\n\nFocus on: {{focus_area}}",
        )
        notes = st.text_input("Notes (optional)", value=default_notes, placeholder="What this prompt is for, known edge cases...")

        detected_vars = extract_variables(prompt_text)
        if detected_vars:
            st.info(f"Variables detected: {', '.join([f'`{{{{{v}}}}}`' for v in detected_vars])}")

        col_save, col_cancel = st.columns(2)
        with col_save:
            if st.button("Save Prompt", type="primary", use_container_width=True):
                if not name or not prompt_text:
                    st.error("Name and prompt text are required.")
                elif editing:
                    update_prompt(editing["id"], name, use_case, prompt_text, notes)
                    st.session_state.pop("edit_prompt", None)
                    st.success("Prompt updated.")
                    st.rerun()
                else:
                    create_prompt(name, use_case, prompt_text, notes)
                    st.success("Prompt saved.")
                    st.rerun()
        with col_cancel:
            if editing and st.button("Cancel", use_container_width=True):
                st.session_state.pop("edit_prompt", None)
                st.rerun()


# ── TAB 2: Test & Refine ──────────────────────────────────────────────────────
with tab_test:
    prompts = get_all_prompts()

    if not prompts:
        st.info("Save a prompt in the Library tab to test it here.")
    else:
        col_sel, col_out = st.columns([1, 1.5], gap="large")

        with col_sel:
            st.subheader("Configure")
            options = {p["name"]: p for p in prompts}
            selected_name = st.selectbox("Select prompt", list(options.keys()))
            selected = options[selected_name]

            st.markdown("**Prompt preview:**")
            st.code(selected["prompt_text"], language="text")

            detected_vars = extract_variables(selected["prompt_text"])
            var_values = {}
            if detected_vars:
                st.markdown("**Fill in variables:**")
                for var in detected_vars:
                    var_values[var] = st.text_area(
                        f"`{{{{{var}}}}}`",
                        placeholder=f"Value for {var}",
                        height=80,
                        key=f"var_{var}",
                    )

            run_btn = st.button("Run Prompt", type="primary", use_container_width=True)

        with col_out:
            st.subheader("Output")
            if run_btn:
                rendered = render_prompt(selected["prompt_text"], var_values)
                with st.spinner("Running via Groq..."):
                    output, latency_ms = run_prompt(rendered, api_key)

                st.markdown(output)
                st.caption(f"{latency_ms} ms · llama-3.3-70b-versatile")

                run_id = save_run(selected["id"], var_values, output, "llama-3.3-70b-versatile", latency_ms)
                st.session_state["last_run_id"] = run_id

                st.divider()
                st.markdown("**Rate this output:**")
                rating = st.feedback("stars", key=f"rating_{run_id}")
                if rating is not None:
                    rate_run(run_id, rating + 1)
                    st.success(f"Rated {rating + 1}/5 — saved.")

                with st.expander("📋 Rendered prompt sent to model"):
                    st.code(rendered, language="text")


# ── TAB 3: Compare Prompts ────────────────────────────────────────────────────
with tab_compare:
    st.subheader("A/B Prompt Comparison")
    st.caption("Run two prompts on the same input and compare outputs side by side.")

    prompts = get_all_prompts()
    if len(prompts) < 2:
        st.info("Save at least 2 prompts in the Library to compare them.")
    else:
        options = {p["name"]: p for p in prompts}
        names = list(options.keys())

        col_a_sel, col_b_sel = st.columns(2)
        with col_a_sel:
            name_a = st.selectbox("Prompt A", names, key="cmp_a")
        with col_b_sel:
            name_b = st.selectbox("Prompt B", names, index=min(1, len(names) - 1), key="cmp_b")

        prompt_a = options[name_a]
        prompt_b = options[name_b]

        all_vars = list(dict.fromkeys(
            extract_variables(prompt_a["prompt_text"]) +
            extract_variables(prompt_b["prompt_text"])
        ))

        shared_values = {}
        if all_vars:
            st.markdown("**Shared variables:**")
            cols = st.columns(min(len(all_vars), 3))
            for i, var in enumerate(all_vars):
                with cols[i % 3]:
                    shared_values[var] = st.text_area(
                        f"`{{{{{var}}}}}`", height=80, key=f"cmp_var_{var}"
                    )

        if st.button("Run Comparison", type="primary"):
            rendered_a = render_prompt(prompt_a["prompt_text"], shared_values)
            rendered_b = render_prompt(prompt_b["prompt_text"], shared_values)

            with st.spinner("Running both prompts..."):
                out_a, lat_a, out_b, lat_b = run_comparison(rendered_a, rendered_b, api_key)

            col_a_out, col_b_out = st.columns(2)
            with col_a_out:
                st.markdown(f"### A: {name_a}")
                st.caption(f"{lat_a} ms")
                st.markdown(out_a)
            with col_b_out:
                st.markdown(f"### B: {name_b}")
                st.caption(f"{lat_b} ms")
                st.markdown(out_b)

            save_run(prompt_a["id"], shared_values, out_a, "llama-3.3-70b-versatile", lat_a)
            save_run(prompt_b["id"], shared_values, out_b, "llama-3.3-70b-versatile", lat_b)

            st.session_state["cmp_out_a"] = out_a
            st.session_state["cmp_out_b"] = out_b
            st.session_state["cmp_name_a"] = name_a
            st.session_state["cmp_name_b"] = name_b

        # AI Judge — shows after comparison is run
        if st.session_state.get("cmp_out_a"):
            st.divider()
            if st.button("Judge Which is Better", type="secondary", use_container_width=True):
                with st.spinner("AI is evaluating both outputs..."):
                    verdict = judge_outputs(
                        st.session_state["cmp_name_a"],
                        st.session_state["cmp_out_a"],
                        st.session_state["cmp_name_b"],
                        st.session_state["cmp_out_b"],
                        api_key,
                    )
                st.success("Judgment complete!")
                st.markdown(verdict)


# ── TAB 4: Run History ────────────────────────────────────────────────────────
with tab_history:
    st.subheader("All Prompt Runs")
    all_runs = get_all_runs()

    if not all_runs:
        st.info("No runs yet. Test a prompt to see history here.")
    else:
        rows = [{"Ran At": r["ran_at"], "Prompt": r["prompt_name"], "Use Case": r["use_case"],
                  "Model": r["model"], "Latency (ms)": r["latency_ms"],
                  "Rating": "★" * int(r["rating"]) if r["rating"] else "—"} for r in all_runs]
        st.dataframe(rows, use_container_width=True)

        avg_latency = sum(r["latency_ms"] for r in all_runs) / len(all_runs)
        rated = [r for r in all_runs if r["rating"]]
        avg_rating = sum(r["rating"] for r in rated) / len(rated) if rated else 0

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Runs", len(all_runs))
        m2.metric("Avg Latency", f"{avg_latency:.0f} ms")
        m3.metric("Avg Rating", f"{avg_rating:.1f} / 5" if avg_rating else "—")
