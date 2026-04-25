"""
Roommie Vilnius — Streamlit frontend  (v1.1)

Run with:  streamlit run app.py
"""

import base64
import streamlit as st

from data.storage import (
    seed_if_empty,
    seed_vilnius_if_missing,
    ensure_social_fields,
    authenticate,
    register_user,
    get_all_users,
    find_record_by_email,
    record_to_user,
    next_user_id,
    record_like,
    get_mutual_matches,
    get_seen_ids,
)
from engine import MatchingEngine
from models import HouseOwner, HouseSeeker

# ---------------------------------------------------------------------------
# Page config  (must be the very first Streamlit call)
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Roommie Vilnius",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Part 1 — CSS  (Gen-Z glassmorphism)
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        /* ── Root typography ───────────────────────────────────── */
        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
        }

        /* ── Gradient background ───────────────────────────────── */
        .stApp,
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%) !important;
            min-height: 100vh;
        }
        [data-testid="stMainBlockContainer"] {
            background: transparent !important;
        }

        /* ── Force ALL text light ──────────────────────────────── */
        html, body,
        p, span, div, li, label, h1, h2, h3, h4, h5, h6,
        .stMarkdown, .stMarkdown p, .stMarkdown span,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3,
        [data-testid="stText"],
        [data-testid="stMarkdownContainer"] p {
            color: #f0f0ff !important;
        }

        /* ── Metric widgets ────────────────────────────────────── */
        [data-testid="stMetricValue"]   { color: #ffffff !important; font-weight: 800 !important; }
        [data-testid="stMetricLabel"] p { color: #b0b0cc !important; font-size: 0.78rem !important; }

        /* ── Caption / small text ──────────────────────────────── */
        [data-testid="stCaptionContainer"] p,
        .stCaption { color: #a0a0cc !important; }

        /* ── Glassmorphism card panels ─────────────────────────── */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(255, 255, 255, 0.07) !important;
            backdrop-filter: blur(14px) !important;
            -webkit-backdrop-filter: blur(14px) !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
            border-radius: 20px !important;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3) !important;
        }

        /* ── Sidebar ───────────────────────────────────────────── */
        [data-testid="stSidebar"] {
            background: rgba(15, 12, 41, 0.7) !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border-right: 1px solid rgba(255, 255, 255, 0.12) !important;
        }
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] span { color: #e0e0ff !important; }

        /* ── Inputs ────────────────────────────────────────────── */
        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"]  textarea {
            background: rgba(255, 255, 255, 0.08) !important;
            color: #f0f0ff !important;
            border: 1px solid rgba(255, 255, 255, 0.2) !important;
            border-radius: 12px !important;
        }

        /* ── Primary button — gradient purple ──────────────────── */
        [data-testid="stBaseButton-primary"],
        [data-testid="stBaseButton-primary"] > button,
        button[kind="primary"] {
            background: linear-gradient(135deg, #7b2ff7 0%, #f107a3 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
            letter-spacing: 0.4px !important;
            box-shadow: 0 4px 20px rgba(123, 47, 247, 0.45) !important;
        }

        /* ── Secondary / default button ────────────────────────── */
        [data-testid="stBaseButton-secondary"],
        [data-testid="stBaseButton-secondary"] > button,
        button[kind="secondary"] {
            background: rgba(255, 255, 255, 0.1) !important;
            color: #f0f0ff !important;
            border: 1px solid rgba(255, 255, 255, 0.25) !important;
            border-radius: 50px !important;
            font-weight: 600 !important;
        }

        /* ── Habit / tier pills ────────────────────────────────── */
        .pill {
            display: inline-block;
            background: rgba(123, 47, 247, 0.25);
            color: #c9a9ff !important;
            border: 1px solid rgba(123, 47, 247, 0.45);
            border-radius: 999px;
            padding: 2px 12px;
            font-size: 0.78rem;
            margin: 2px;
            font-weight: 600;
        }
        .badge-perfect {
            background: rgba(39, 174, 96, 0.25);
            color: #7dffb2 !important;
            border: 1px solid rgba(39, 174, 96, 0.5);
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 700;
        }
        .badge-suggested {
            background: rgba(241, 196, 15, 0.2);
            color: #ffe57f !important;
            border: 1px solid rgba(241, 196, 15, 0.4);
            padding: 3px 12px;
            border-radius: 999px;
            font-size: 0.82rem;
            font-weight: 700;
        }

        /* ── Discovery card ────────────────────────────────────── */
        .disc-card {
            background: rgba(255, 255, 255, 0.06);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.14);
            border-radius: 24px;
            box-shadow: 0 8px 40px rgba(0, 0, 0, 0.35);
            padding: 28px 32px;
            max-width: 680px;
            margin: 0 auto;
        }
        .disc-card h2, .disc-card p, .disc-card span { color: #f0f0ff !important; }
        .disc-name   { font-size: 1.9rem; font-weight: 800; color: #ffffff !important; margin-bottom: 2px; }
        .disc-sub    { font-size: 1rem;   color: #b0b0cc !important; margin-bottom: 10px; }
        .disc-bio    { font-style: italic; color: #c0c0e0 !important; margin: 10px 0; }
        .disc-detail { font-size: 0.9rem; color: #d0d0f0 !important; margin: 6px 0; }

        /* ── Progress bar — gradient ───────────────────────────── */
        [data-testid="stProgress"] > div > div {
            background: linear-gradient(90deg, #7b2ff7, #f107a3) !important;
        }

        /* ── Divider ───────────────────────────────────────────── */
        hr { border-color: rgba(255, 255, 255, 0.12) !important; }

        /* ── Tab styling ───────────────────────────────────────── */
        [data-testid="stTabs"] [data-baseweb="tab"] {
            color: #a0a0cc !important;
            font-weight: 600 !important;
        }
        [data-testid="stTabs"] [aria-selected="true"] {
            color: #c9a9ff !important;
            border-bottom-color: #7b2ff7 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Bootstrap storage & session state
# ---------------------------------------------------------------------------

seed_if_empty()
seed_vilnius_if_missing()
ensure_social_fields()

for _key, _default in [
    ("user",        None),
    ("candidates",  []),       # list of (User, score, label)
    ("disliked_ids", set()),   # disliked this session only
    ("just_matched", None),    # name of the user we just mutually matched with
    ("cands_uid",   None),     # user_id the candidates were built for
]:
    if _key not in st.session_state:
        st.session_state[_key] = _default

# ---------------------------------------------------------------------------
# Avatar helpers
# ---------------------------------------------------------------------------

_ROLE_COLOURS = {"HouseOwner": "#4A90E2", "HouseSeeker": "#E2824A"}


def _svg_avatar(initial: str, colour: str, size: int) -> str:
    half = size // 2
    font = int(size * 0.42)
    svg = (
        f'<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="{half}" cy="{half}" r="{half}" fill="{colour}"/>'
        f'<text x="50%" y="50%" dominant-baseline="central" text-anchor="middle" '
        f'font-size="{font}" font-family="Arial,sans-serif" fill="white" font-weight="bold">'
        f"{initial}</text></svg>"
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


def _avatar_src(user) -> str:
    if user.avatar_url:
        return user.avatar_url
    return _svg_avatar(
        user.name[0].upper(),
        _ROLE_COLOURS.get(type(user).__name__, "#888"),
        160,
    )


# ---------------------------------------------------------------------------
# Shared UI helpers
# ---------------------------------------------------------------------------

def _pills(items: list[str]) -> str:
    return " ".join(f'<span class="pill">{i}</span>' for i in items)


def _clamped_progress(value: float, max_val: float) -> None:
    st.progress(max(0.0, min(1.0, value / max_val if max_val else 0.0)))


def _tier_badge(label: str) -> str:
    cls  = "badge-perfect" if label == "Perfect" else "badge-suggested"
    icon = "✔" if label == "Perfect" else "~"
    return f'<span class="{cls}">{icon}&nbsp;{label}</span>'


# ---------------------------------------------------------------------------
# Part 2 — Discovery feed
# ---------------------------------------------------------------------------

def _init_candidates(user) -> None:
    """Build the candidate queue once per login session."""
    if st.session_state.cands_uid == user.user_id:
        return
    engine  = MatchingEngine()
    matches = engine.find_matches(user, get_all_users())
    st.session_state.candidates  = matches
    st.session_state.cands_uid   = user.user_id
    st.session_state.disliked_ids = set()
    st.session_state.just_matched = None


def render_discovery(user) -> None:
    _init_candidates(user)

    # ── Mutual match celebration (one render only) ──────────────────────────
    if st.session_state.just_matched:
        matched_name = st.session_state.just_matched
        st.balloons()
        st.markdown(
            f"""
            <div style="text-align:center;padding:24px;background:#d4edda;
                        border-radius:16px;border:2px solid #28a745;margin-bottom:20px;">
                <div style="font-size:3rem;">🎉</div>
                <div style="font-size:1.6rem;font-weight:700;color:#155724 !important;">
                    It's a Match!
                </div>
                <div style="font-size:1.1rem;color:#155724 !important;margin-top:6px;">
                    You and <strong>{matched_name}</strong> liked each other!
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.session_state.just_matched = None

    # ── Filter out already-seen candidates ──────────────────────────────────
    seen_ids = get_seen_ids(user.user_id) | st.session_state.disliked_ids
    queue    = [(m, s, l) for m, s, l in st.session_state.candidates
                if m.user_id not in seen_ids]

    if not queue:
        st.markdown(
            """
            <div style="text-align:center;padding:40px;color:#555555;">
                <div style="font-size:2.5rem;">🏙️</div>
                <div style="font-size:1.2rem;font-weight:600;margin-top:8px;">
                    You've seen everyone in Vilnius!
                </div>
                <div style="margin-top:6px;color:#888;">
                    Check your Matches tab or come back later.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    candidate, score, label = queue[0]
    remaining = len(queue)

    # ── Progress indicator ───────────────────────────────────────────────────
    total = len(st.session_state.candidates)
    seen_count = total - remaining
    st.caption(f"Candidate {seen_count + 1} of {total}")
    st.progress(seen_count / total if total else 0.0)
    st.markdown("")

    # ── Discovery card ───────────────────────────────────────────────────────
    role_str = "House Owner" if isinstance(candidate, HouseOwner) else "House Seeker"

    location_line = candidate.get_detail()

    engine    = MatchingEngine()
    breakdown = engine.score_breakdown(user, candidate)
    shared    = set(user.habits) & set(candidate.habits)

    col_card, col_score = st.columns([3, 2], gap="large")

    with col_card:
        st.markdown(
            f"""
            <div class="disc-card">
                <div style="display:flex;align-items:center;gap:18px;margin-bottom:14px;">
                    <img src="{_avatar_src(candidate)}" width="90" height="90"
                         style="border-radius:50%;object-fit:cover;flex-shrink:0;">
                    <div>
                        <div class="disc-name">{candidate.name}</div>
                        <div class="disc-sub">{role_str} &nbsp;·&nbsp; {candidate.occupation}
                             &nbsp;·&nbsp; Age {candidate.age}</div>
                        {_tier_badge(label)}
                    </div>
                </div>
                <p class="disc-bio">"{candidate.bio}"</p>
                <p class="disc-detail">{location_line}</p>
                <p class="disc-detail">🗣 {" · ".join(candidate.languages)}</p>
                <div style="margin-top:10px;">{_pills(candidate.habits)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_score:
        with st.container(border=True):
            st.markdown(
                f"<div style='text-align:center;font-size:2rem;font-weight:700;"
                f"color:#1a1a2e;'>{score:.1f}%</div>"
                f"<div style='text-align:center;color:#555;font-size:0.85rem;"
                f"margin-bottom:10px;'>Compatibility</div>",
                unsafe_allow_html=True,
            )
            _clamped_progress(score, 100)

            st.markdown("---")
            st.caption(f"Habits  {breakdown['habits']:.1f} / 70")
            _clamped_progress(breakdown["habits"], 70)

            st.caption(f"Languages  {breakdown['languages']:.1f} / 20")
            _clamped_progress(breakdown["languages"], 20)

            st.caption(f"Vibe  {breakdown['vibe']:.1f} / 10")
            _clamped_progress(breakdown["vibe"], 10)

            if breakdown["vibe"] > 0:
                st.success("✦ Vibe Match!")

            if shared:
                st.markdown("**Shared:**")
                st.markdown(_pills(sorted(shared)), unsafe_allow_html=True)

    # ── Like / Dislike buttons ───────────────────────────────────────────────
    st.markdown("")
    btn_col1, btn_col2, btn_col3 = st.columns([2, 1, 2])

    with btn_col1:
        if st.button("✅  Like", use_container_width=True, key="btn_like",
                     type="primary"):
            is_mutual = record_like(user.user_id, candidate.user_id)
            if is_mutual:
                st.session_state.just_matched = candidate.name
            st.rerun()

    with btn_col3:
        if st.button("❌  Dislike", use_container_width=True, key="btn_dislike"):
            st.session_state.disliked_ids.add(candidate.user_id)
            st.rerun()


# ---------------------------------------------------------------------------
# Mutual Matches tab
# ---------------------------------------------------------------------------

def render_mutual_matches(user) -> None:
    mutual = get_mutual_matches(user.user_id)

    if not mutual:
        st.markdown(
            """
            <div style="text-align:center;padding:40px;color:#666;">
                <div style="font-size:2.5rem;">💔</div>
                <div style="font-size:1.1rem;font-weight:600;margin-top:8px;">
                    No mutual matches yet
                </div>
                <div style="color:#888;margin-top:4px;">
                    Head to Discover and start liking people!
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    st.markdown(f"### {len(mutual)} mutual match{'es' if len(mutual) != 1 else ''}")
    engine = MatchingEngine()

    for match in mutual:
        role_str = "House Owner" if isinstance(match, HouseOwner) else "House Seeker"
        breakdown = engine.score_breakdown(user, match)
        shared    = set(user.habits) & set(match.habits)
        score     = breakdown["total"]

        with st.container(border=True):
            c_av, c_info, c_score = st.columns([1, 3, 2], gap="medium")

            with c_av:
                st.markdown(
                    f'<img src="{_avatar_src(match)}" width="72" height="72" '
                    f'style="border-radius:50%;object-fit:cover;">',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    '<span class="badge-perfect">💚 Matched</span>',
                    unsafe_allow_html=True,
                )

            with c_info:
                st.markdown(f"### {match.name}")
                st.markdown(f"**{role_str}** · {match.occupation} · Age {match.age}")
                st.markdown(f"*{match.bio}*")
                st.markdown(match.get_detail())
                if shared:
                    st.markdown("**Shared habits:** " + _pills(sorted(shared)),
                                unsafe_allow_html=True)

            with c_score:
                st.metric("Compatibility", f"{score:.1f}%")
                _clamped_progress(score, 100)
                st.caption(f"Habits {breakdown['habits']:.1f} · "
                           f"Lang {breakdown['languages']:.1f} · "
                           f"Vibe {breakdown['vibe']:.1f}")
                if breakdown["vibe"] > 0:
                    st.success("✦ Vibe Match!")


# ---------------------------------------------------------------------------
# Profile card (sidebar / compact)
# ---------------------------------------------------------------------------

def render_profile_card(user) -> None:
    role = "House Owner" if isinstance(user, HouseOwner) else "House Seeker"
    col_av, col_info = st.columns([1, 5], gap="medium")
    with col_av:
        st.markdown(
            f'<img src="{_avatar_src(user)}" width="80" height="80" '
            f'style="border-radius:50%;object-fit:cover;">',
            unsafe_allow_html=True,
        )
    with col_info:
        st.markdown(f"### {user.name}")
        st.markdown(f"**{role}** · {user.occupation} · Age {user.age} · {user.gender.capitalize()}")
        st.markdown(f"*{user.bio}*")
        st.markdown(_pills(user.habits), unsafe_allow_html=True)
        st.caption(f"🗣 {' · '.join(user.languages)}")
        st.markdown(user.get_detail())


# ---------------------------------------------------------------------------
# Dashboard (logged-in view)
# ---------------------------------------------------------------------------

def render_dashboard(user) -> None:
    # ── Profile summary ──────────────────────────────────────────────────────
    with st.container(border=True):
        render_profile_card(user)

    st.markdown("")

    # ── Count mutual matches for tab label ───────────────────────────────────
    mutual_count = len(get_mutual_matches(user.user_id))
    match_label  = f"💚 My Matches ({mutual_count})" if mutual_count else "💚 My Matches"

    tab_disc, tab_matches = st.tabs(["🔍 Discover", match_label])

    with tab_disc:
        render_discovery(user)

    with tab_matches:
        render_mutual_matches(user)


# ---------------------------------------------------------------------------
# Landing page (logged-out)
# ---------------------------------------------------------------------------

def render_landing() -> None:
    st.markdown("# 🏠 Roommie Vilnius")
    st.markdown("### Find your ideal roommate in the heart of Vilnius.")
    st.info("👈 **Login** or **Sign Up** in the sidebar to get started.")

    all_users = get_all_users()
    owners  = sum(1 for u in all_users if isinstance(u, HouseOwner))
    seekers = sum(1 for u in all_users if isinstance(u, HouseSeeker))

    c1, c2, c3 = st.columns(3)
    c1.metric("Registered Users", len(all_users))
    c2.metric("House Owners",     owners)
    c3.metric("House Seekers",    seekers)


# ---------------------------------------------------------------------------
# Sidebar — auth
# ---------------------------------------------------------------------------

def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("## 🏠 Roommie")

        if st.session_state.user is not None:
            user = st.session_state.user
            role = "House Owner" if isinstance(user, HouseOwner) else "House Seeker"
            st.markdown(
                f'<img src="{_avatar_src(user)}" width="56" height="56" '
                f'style="border-radius:50%;object-fit:cover;margin-bottom:8px;">',
                unsafe_allow_html=True,
            )
            st.markdown(f"**{user.name}**")
            st.caption(role)
            st.divider()
            if st.button("Log out", use_container_width=True):
                for k in ("user", "candidates", "disliked_ids",
                          "just_matched", "cands_uid"):
                    st.session_state[k] = None if k == "user" else \
                                          [] if k == "candidates" else \
                                          set() if k == "disliked_ids" else None
                st.rerun()
            return

        tab_login, tab_signup = st.tabs(["Login", "Sign Up"])
        with tab_login:
            _render_login()
        with tab_signup:
            _render_signup()


def _render_login() -> None:
    st.subheader("Welcome back")
    email    = st.text_input("Email",    key="li_email")
    password = st.text_input("Password", key="li_password", type="password")

    if st.button("Login", use_container_width=True, key="btn_login"):
        if not email or not password:
            st.error("Please fill in both fields.")
            return
        record = authenticate(email, password)
        if record:
            st.session_state.user = record_to_user(record)
            st.rerun()
        else:
            st.error("Incorrect email or password.")


def _render_signup() -> None:
    st.subheader("Create account")

    email      = st.text_input("Email",                        key="su_email")
    password   = st.text_input("Password (min 6 chars)", type="password", key="su_password")
    st.markdown("**Profile**")
    name       = st.text_input("Full name",   key="su_name")
    age        = st.number_input("Age", min_value=16, max_value=120, value=22, key="su_age")
    gender     = st.selectbox("Gender",
                              ["Male", "Female", "Non-binary", "Prefer not to say"],
                              key="su_gender")
    occupation = st.text_input("Occupation",  key="su_occupation")
    bio        = st.text_area("Short bio",    key="su_bio", height=80)
    habits_raw = st.text_input("Habits (comma-separated)",
                               placeholder="Clean, Quiet, Non-smoker", key="su_habits")
    langs_raw  = st.text_input("Languages (comma-separated)",
                               placeholder="Lithuanian, English",       key="su_langs")
    avatar_url = st.text_input("Avatar image URL (optional)",           key="su_avatar")

    st.markdown("**Role**")
    role = st.radio("I am a ...", ["House Owner", "House Seeker"],
                    horizontal=True, key="su_role")

    neighborhood, monthly_rent, max_budget = "", 0, 0
    preferred_neighborhoods: list[str] = []

    if role == "House Owner":
        neighborhood = st.text_input("Neighbourhood", key="su_neighborhood")
        monthly_rent = st.number_input("Monthly rent (€)",
                                       min_value=1, max_value=100_000, value=500,
                                       key="su_rent")
    else:
        max_budget = st.number_input("Max monthly budget (€)",
                                     min_value=1, max_value=100_000, value=500,
                                     key="su_budget")
        pn_raw = st.text_input("Preferred neighbourhoods (comma-separated)",
                               placeholder="Užupis, Šnipiškės", key="su_pn")
        preferred_neighborhoods = [n.strip() for n in pn_raw.split(",") if n.strip()]

    if st.button("Create Account", use_container_width=True, key="btn_signup"):
        habits    = [h.strip() for h in habits_raw.split(",") if h.strip()]
        languages = [l.strip() for l in langs_raw.split(",")  if l.strip()]

        errors: list[str] = []
        if not email:         errors.append("Email is required.")
        if len(password) < 6: errors.append("Password must be at least 6 characters.")
        if not name:          errors.append("Name is required.")
        if not occupation:    errors.append("Occupation is required.")
        if not bio:           errors.append("Bio is required.")
        if not habits:        errors.append("Enter at least one habit.")
        if not languages:     errors.append("Enter at least one language.")
        if role == "House Owner" and not neighborhood:
            errors.append("Neighbourhood is required.")
        if role == "House Seeker" and not preferred_neighborhoods:
            errors.append("Enter at least one preferred neighbourhood.")

        if errors:
            for msg in errors:
                st.error(msg)
            return

        if find_record_by_email(email):
            st.error("That email is already registered — try logging in.")
            return

        uid = next_user_id()
        if role == "House Owner":
            new_user = HouseOwner(
                user_id=uid, name=name, age=int(age), gender=gender.lower(),
                occupation=occupation, bio=bio, avatar_url=avatar_url,
                habits=habits, languages=languages,
                neighborhood=neighborhood, monthly_rent=int(monthly_rent),
            )
        else:
            new_user = HouseSeeker(
                user_id=uid, name=name, age=int(age), gender=gender.lower(),
                occupation=occupation, bio=bio, avatar_url=avatar_url,
                habits=habits, languages=languages,
                max_budget=int(max_budget),
                preferred_neighborhoods=preferred_neighborhoods,
            )

        try:
            register_user(new_user, email, password)
            st.session_state.user = new_user
            st.rerun()
        except ValueError as exc:
            st.error(str(exc))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

render_sidebar()

if st.session_state.user is None:
    render_landing()
else:
    render_dashboard(st.session_state.user)
