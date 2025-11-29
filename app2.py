import streamlit as st
import requests
import json
from datetime import datetime, timedelta
import random

# =========================
# Groq API CONFIG
# =========================
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Page configuration
st.set_page_config(
    page_title="Social Media Agent",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    .content-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin: 15px 0;
        border-left: 5px solid #667eea;
    }
    .caption-box {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border: 2px dashed #667eea;
        margin: 10px 0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .hashtag {
        color: #667eea;
        font-weight: bold;
    }
    .platform-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        margin: 5px 5px 5px 0;
    }
    .instagram-badge { background: linear-gradient(45deg, #f09433, #e6683c, #dc2743, #cc2366, #bc1888); color: white; }
    .twitter-badge { background: #1DA1F2; color: white; }
    .linkedin-badge { background: #0077b5; color: white; }
    .facebook-badge { background: #1877f2; color: white; }
    .tiktok-badge { background: #000000; color: white; }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 10px 0;
    }
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        width: 100%;
    }
    .calendar-day {
        background: white;
        padding: 15px;
        border-radius: 8px;
        margin: 5px 0;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''

if 'generated_content' not in st.session_state:
    st.session_state.generated_content = []

if 'content_calendar' not in st.session_state:
    st.session_state.content_calendar = []

if 'brand_info' not in st.session_state:
    st.session_state.brand_info = {
        'name': '',
        'industry': '',
        'tone': 'Professional',
        'target_audience': ''
    }

# =========================
# GROQ HELPER - FIXED VERSION
# =========================
def call_groq_api(prompt, api_key, max_tokens=800, temperature=0.8):
    """Call Groq Chat Completions API with improved error handling"""
    try:
        # Validate API key
        if not api_key or len(api_key.strip()) == 0:
            st.error("❌ API key is empty. Please enter a valid Groq API key.")
            return None
        
        # Clean the API key
        api_key = api_key.strip()
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # Ensure parameters are correct types
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert social media content creator. Generate engaging, creative, and platform-optimized content."
                },
                {
                    "role": "user",
                    "content": str(prompt)
                }
            ],
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
            "top_p": 1,
            "stream": False
        }

        response = requests.post(
            GROQ_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )

        # Handle successful response
        if response.status_code == 200:
            data = response.json()
            if 'choices' in data and len(data['choices']) > 0:
                return data["choices"][0]["message"]["content"]
            else:
                st.error("❌ Unexpected API response format")
                return None

        # Handle error responses
        try:
            err_body = response.json()
            error_message = err_body.get('error', {}).get('message', str(err_body))
        except Exception:
            error_message = response.text

        if response.status_code == 400:
            st.error(f"❌ Bad Request (400): The request was invalid.\n\n**Possible causes:**\n- Invalid model name\n- Incorrect parameter format\n- Malformed request\n\n**Details:** {error_message}")
        elif response.status_code == 401:
            st.error(f"❌ Unauthorized (401): Invalid API key.\n\n**Please check:**\n- Your API key is correct\n- The key hasn't expired\n- You copied the entire key without spaces\n\n**Details:** {error_message}")
        elif response.status_code == 429:
            st.error(f"⚠️ Rate Limit (429): Too many requests.\n\nPlease wait a moment and try again.\n\n**Details:** {error_message}")
        elif response.status_code == 503:
            st.error(f"⚠️ Service Unavailable (503): Groq servers are temporarily unavailable.\n\nPlease try again in a few moments.\n\n**Details:** {error_message}")
        else:
            st.error(f"❌ API Error {response.status_code}: {error_message}")
        
        return None

    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. The API took too long to respond. Please try again.")
        return None
    except requests.exceptions.ConnectionError:
        st.error("🌐 Connection error. Please check your internet connection and try again.")
        return None
    except json.JSONDecodeError:
        st.error("❌ Failed to parse API response. The response was not valid JSON.")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None

# =========================
# GENERATION FUNCTIONS
# =========================
def generate_content_ideas(topic, platform, count, api_key, brand_info):
    """Generate content ideas using Groq API"""

    # Fallback content ideas if API fails
    fallback_ideas = {
        'Instagram': [
            f"1. Behind-the-scenes: Show your process for {topic}",
            f"2. Quick tips carousel: Top 5 ways to improve your {topic}",
            f"3. Before/after transformation related to {topic}",
            f"4. User-generated content featuring {topic}",
            f"5. Story poll: Ask audience about their {topic} preferences",
            f"6. Reels tutorial: Step-by-step guide on {topic}",
            f"7. Throwback post: Your journey with {topic}",
            f"8. Collaboration post with influencer about {topic}",
            f"9. Myth-busting: Common misconceptions about {topic}",
            f"10. Motivational quote related to {topic}"
        ],
        'Twitter': [
            f"1. Thread: 10 game-changing facts about {topic}",
            f"2. Poll: What's your biggest challenge with {topic}?",
            f"3. Hot take: Controversial opinion on {topic}",
            f"4. Quick tip: One-liner advice about {topic}",
            f"5. Ask Twitter: What's your experience with {topic}?",
            f"6. Statistic tweet: Surprising data about {topic}",
            f"7. Quote tweet: React to industry news about {topic}",
            f"8. Meme: Relatable humor about {topic}",
            f"9. Resource thread: Best tools for {topic}",
            f"10. Success story: Customer win with {topic}"
        ],
        'LinkedIn': [
            f"1. Thought leadership: Industry trends in {topic}",
            f"2. Case study: How we helped client with {topic}",
            f"3. Personal story: Lessons learned from {topic}",
            f"4. Infographic: Key statistics about {topic}",
            f"5. Team spotlight: Expert discussing {topic}",
            f"6. Industry insight: Future predictions for {topic}",
            f"7. How-to article: Professional guide to {topic}",
            f"8. Company achievement related to {topic}",
            f"9. Expert interview: Q&A about {topic}",
            f"10. Resource share: Free guide on {topic}"
        ]
    }

    prompt = f"""Generate {count} creative social media content ideas for {platform}.

Topic: {topic}
Brand: {brand_info['name'] or 'Your Brand'}
Industry: {brand_info['industry']}
Tone: {brand_info['tone']}
Target Audience: {brand_info['target_audience'] or 'General audience'}

For each idea, provide:
1. A catchy title
2. Main concept/angle
3. Content type (carousel, video, image, text)
4. Engagement hook

Format as a numbered list with clear separation between ideas."""

    if api_key:
        with st.spinner('🎨 Generating content ideas with AI...'):
            result = call_groq_api(prompt, api_key, max_tokens=800, temperature=0.8)
            if result:
                return result
            else:
                st.warning("⚠️ API request failed. Showing fallback ideas instead.")
                ideas_list = fallback_ideas.get(platform, fallback_ideas['Instagram'])
                return '\n\n'.join(ideas_list[:count])
    else:
        st.info("💡 Using template-based ideas. Add API key for AI-generated content!")
        ideas_list = fallback_ideas.get(platform, fallback_ideas['Instagram'])
        return '\n\n'.join(ideas_list[:count])

def generate_caption(idea, platform, api_key, brand_info):
    """Generate caption for specific content idea"""

    # Fallback caption template
    def create_fallback_caption(idea, platform):
        emojis = {
            'Instagram': '✨💫🌟',
            'Twitter': '🔥💡🚀',
            'LinkedIn': '💼📊🎯',
            'Facebook': '👥💬❤️'
        }

        hashtags = {
            'Instagram': '#ContentCreation #SocialMedia #Marketing #Business #Growth',
            'Twitter': '#ContentMarketing #SocialMediaTips #Growth',
            'LinkedIn': '#Marketing #Business #ContentStrategy #Growth',
            'Facebook': '#Business #Marketing #SocialMedia'
        }

        emoji = emojis.get(platform, '✨')
        tags = hashtags.get(platform, '#Marketing #Business')

        caption = f"{emoji} {idea}\n\n"
        caption += "What do you think? Let us know in the comments! 👇\n\n"
        caption += tags
        return caption

    prompt = f"""Create an engaging {platform} caption for this content idea:

{idea}

Brand: {brand_info['name'] or 'Your Brand'}
Tone: {brand_info['tone']}
Target Audience: {brand_info['target_audience'] or 'General audience'}

Requirements:
- Platform-optimized length
- Include call-to-action
- Add relevant emojis
- Suggest 5-10 hashtags
- Engaging and on-brand"""

    if api_key:
        with st.spinner('✍️ Writing caption with AI...'):
            result = call_groq_api(prompt, api_key, max_tokens=400, temperature=0.8)
            if result:
                return result
            else:
                st.warning("⚠️ Using template caption. Add API key for custom AI captions!")
                return create_fallback_caption(idea, platform)
    else:
        st.info("💡 Using template caption. Add API key for AI-generated captions!")
        return create_fallback_caption(idea, platform)

def generate_weekly_plan(topic, platforms, api_key, brand_info):
    """Generate 7-day content calendar"""

    # Fallback calendar template
    def create_fallback_calendar(topic, platforms):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        times = ['9:00 AM', '12:00 PM', '3:00 PM', '6:00 PM', '10:00 AM', '1:00 PM', '7:00 PM']
        content_types = ['Image Post', 'Video', 'Carousel', 'Story/Tweet', 'Infographic', 'Behind-the-scenes', 'User Content']

        calendar = f"7-Day Content Calendar: {topic}\n\n"

        for i, day in enumerate(days):
            platform = platforms[i % len(platforms)]
            time = times[i]
            ctype = content_types[i]

            calendar += f"📅 {day} | {platform} | {time}\n"
            calendar += f"   Type: {ctype}\n"
            calendar += f"   Idea: Share insights about {topic}\n"
            calendar += f"   Goal: Engage and educate audience\n\n"

        return calendar

    prompt = f"""Create a 7-day social media content calendar.

Topic/Theme: {topic}
Platforms: {', '.join(platforms)}
Brand: {brand_info['name'] or 'Your Brand'}
Industry: {brand_info['industry']}

For each day, provide:
- Day and best posting time
- Platform
- Content type
- Post idea (brief)
- Key message

Format as: Day | Platform | Time | Content Type | Idea"""

    if api_key:
        with st.spinner('📅 Creating content calendar with AI...'):
            result = call_groq_api(prompt, api_key, max_tokens=1200, temperature=0.7)
            if result:
                return result
            else:
                st.warning("⚠️ Using template calendar. Add API key for custom AI calendar!")
                return create_fallback_calendar(topic, platforms)
    else:
        st.info("💡 Using template calendar. Add API key for AI-generated calendar!")
        return create_fallback_calendar(topic, platforms)

def get_platform_badge(platform):
    """Return HTML badge for platform"""
    badges = {
        'Instagram': '<span class="platform-badge instagram-badge">📸 Instagram</span>',
        'Twitter': '<span class="platform-badge twitter-badge">🐦 Twitter</span>',
        'LinkedIn': '<span class="platform-badge linkedin-badge">💼 LinkedIn</span>',
        'Facebook': '<span class="platform-badge facebook-badge">👥 Facebook</span>',
        'TikTok': '<span class="platform-badge tiktok-badge">🎵 TikTok</span>'
    }
    return badges.get(platform, '')

# =========================
# SIDEBAR
# =========================
with st.sidebar:
    st.markdown("### 🔑 API Configuration")
    
    # Add helpful information
    with st.expander("ℹ️ How to get Groq API Key", expanded=False):
        st.markdown("""
        1. Go to [console.groq.com](https://console.groq.com)
        2. Sign up or log in
        3. Navigate to API Keys section
        4. Create a new API key
        5. Copy and paste it below
        """)
    
    api_key_input = st.text_input(
        "Groq API Key",
        type="password",
        value=st.session_state.api_key,
        help="Enter your Groq API key from console.groq.com"
    )

    if st.button("💾 Save API Key"):
        if api_key_input.strip():
            st.session_state.api_key = api_key_input.strip()
            st.success("✅ API Key saved!")
        else:
            st.error("❌ Please enter a valid API key!")

    # Test API connection
    if st.session_state.api_key:
        if st.button("🧪 Test API Connection"):
            with st.spinner("Testing..."):
                test_result = call_groq_api(
                    "Say 'Hello! API is working correctly.' in one short sentence.",
                    st.session_state.api_key,
                    max_tokens=50,
                    temperature=0.5
                )
                if test_result:
                    st.success(f"✅ Connection successful!\n\n{test_result}")

    st.markdown("---")

    st.markdown("### 🎯 Brand Information")
    st.session_state.brand_info['name'] = st.text_input(
        "Brand Name",
        value=st.session_state.brand_info['name'],
        placeholder="e.g., TechStartup"
    )

    st.session_state.brand_info['industry'] = st.selectbox(
        "Industry",
        ["Technology", "Fashion", "Food & Beverage", "Fitness", "Education",
         "Travel", "Finance", "Healthcare", "E-commerce", "Other"]
    )

    st.session_state.brand_info['tone'] = st.select_slider(
        "Brand Tone",
        options=["Professional", "Friendly", "Casual", "Playful", "Inspirational"]
    )

    st.session_state.brand_info['target_audience'] = st.text_input(
        "Target Audience",
        value=st.session_state.brand_info['target_audience'],
        placeholder="e.g., Young professionals 25-35"
    )

    st.markdown("---")

    st.markdown("### 📊 Quick Stats")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Ideas Generated", len(st.session_state.generated_content))
    with col2:
        st.metric("Plans Created", len(st.session_state.content_calendar))

    st.markdown("---")

    if st.button("🗑️ Clear All Data"):
        st.session_state.generated_content = []
        st.session_state.content_calendar = []
        st.success("✅ Data cleared!")
        st.rerun()

# =========================
# MAIN HEADER
# =========================
st.markdown('''
<div class="main-header">
    <h1>📱 Social Media Agent</h1>
    <p>AI-Powered Content Ideas, Captions & Planning</p>
</div>
''', unsafe_allow_html=True)

# Create tabs (4 tabs now)
tab1, tab2, tab3, tab4 = st.tabs(
    ["💡 Content Ideas", "✍️ Caption Generator", "📅 Content Calendar", "🚀 Generate & Plan"]
)

# =========================
# TAB 1: CONTENT IDEAS
# =========================
with tab1:
    st.markdown("## 💡 Generate Content Ideas")

    col1, col2 = st.columns([2, 1])

    with col1:
        topic = st.text_input(
            "What topic or theme?",
            placeholder="e.g., Productivity tips for remote workers"
        )

    with col2:
        platform = st.selectbox(
            "Platform",
            ["Instagram", "Twitter", "LinkedIn", "Facebook", "TikTok", "All Platforms"]
        )

    col1, col2 = st.columns([1, 1])
    with col1:
        num_ideas = st.slider("Number of ideas", 3, 10, 5)

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Generate Ideas", use_container_width=True):
            if not st.session_state.api_key:
                st.warning("⚠️ Please enter your Groq API key in the sidebar first!")
            elif not topic:
                st.warning("⚠️ Please enter a topic!")
            else:
                ideas = generate_content_ideas(
                    topic,
                    platform,
                    num_ideas,
                    st.session_state.api_key,
                    st.session_state.brand_info
                )

                if ideas:
                    st.session_state.generated_content.append({
                        'timestamp': datetime.now(),
                        'topic': topic,
                        'platform': platform,
                        'ideas': ideas
                    })
                    st.success("✅ Content ideas generated!")

    # Display generated ideas
    if st.session_state.generated_content:
        st.markdown("---")
        st.markdown("### 📝 Generated Ideas")

        for idx, content in enumerate(reversed(st.session_state.generated_content)):
            with st.expander(
                f"💡 {content['topic']} - {content['platform']} ({content['timestamp'].strftime('%Y-%m-%d %H:%M')})"
            ):
                st.markdown(get_platform_badge(content['platform']), unsafe_allow_html=True)
                st.markdown(f"<div class='content-card'>{content['ideas']}</div>", unsafe_allow_html=True)

                if st.button(f"📋 Copy Ideas", key=f"copy_{idx}"):
                    st.code(content['ideas'], language=None)

# =========================
# TAB 2: CAPTION GENERATOR
# =========================
with tab2:
    st.markdown("## ✍️ Generate Captions")

    col1, col2 = st.columns([2, 1])

    with col1:
        caption_idea = st.text_area(
            "Content Idea or Description",
            placeholder="e.g., Announcing our new product launch - eco-friendly water bottles",
            height=100
        )

    with col2:
        caption_platform = st.selectbox(
            "Platform",
            ["Instagram", "Twitter", "LinkedIn", "Facebook"],
            key="caption_platform"
        )

        if st.button("✨ Generate Caption", use_container_width=True):
            if not st.session_state.api_key:
                st.warning("⚠️ Please enter your Groq API key!")
            elif not caption_idea:
                st.warning("⚠️ Please describe your content idea!")
            else:
                caption = generate_caption(
                    caption_idea,
                    caption_platform,
                    st.session_state.api_key,
                    st.session_state.brand_info
                )

                if caption:
                    st.markdown("---")
                    st.markdown("### 📱 Your Caption")
                    st.markdown(get_platform_badge(caption_platform), unsafe_allow_html=True)
                    st.markdown(f"<div class='caption-box'>{caption}</div>", unsafe_allow_html=True)

                    col1b, col2b = st.columns(2)
                    with col1b:
                        if st.button("📋 Copy Caption"):
                            st.code(caption, language=None)
                    with col2b:
                        if st.button("🔄 Generate Another"):
                            st.rerun()

# =========================
# TAB 3: CONTENT CALENDAR
# =========================
with tab3:
    st.markdown("## 📅 Weekly Content Planner")

    col1, col2 = st.columns([2, 1])

    with col1:
        calendar_topic = st.text_input(
            "Theme for the week",
            placeholder="e.g., Summer fitness challenge"
        )

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)

    # Date range selection
    st.markdown("### 📆 Select Date Range")
    dr_col1, dr_col2 = st.columns(2)
    with dr_col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now().date(),
            key="cal_start_date"
        )
    with dr_col2:
        end_date = st.date_input(
            "End Date",
            value=(datetime.now() + timedelta(days=6)).date(),
            key="cal_end_date"
        )

    # Validate date range
    if start_date > end_date:
        st.error("❌ Start date cannot be after end date!")
        date_range_valid = False
    else:
        days_diff = (end_date - start_date).days + 1
        st.info(
            f"📅 Calendar period: {days_diff} days "
            f"({start_date.strftime('%b %d, %Y')} to {end_date.strftime('%b %d, %Y')})"
        )
        date_range_valid = True

    platforms_selected = st.multiselect(
        "Select platforms for this calendar",
        ["Instagram", "Twitter", "LinkedIn", "Facebook", "TikTok"],
        default=["Instagram", "Twitter"]
    )

    if st.button("📅 Create Calendar", use_container_width=True):
        if not st.session_state.api_key:
            st.warning("⚠️ Please enter your Groq API key!")
        elif not calendar_topic:
            st.warning("⚠️ Please enter a theme!")
        elif not platforms_selected:
            st.warning("⚠️ Please select at least one platform!")
        elif not date_range_valid:
            st.warning("⚠️ Please select a valid date range!")
        else:
            calendar = generate_weekly_plan(
                calendar_topic,
                platforms_selected,
                st.session_state.api_key,
                st.session_state.brand_info
            )

            if calendar:
                st.session_state.content_calendar.append({
                    'timestamp': datetime.now(),
                    'topic': calendar_topic,
                    'platforms': platforms_selected,
                    'calendar': calendar,
                    'start_date': start_date,
                    'end_date': end_date
                })
                st.success("✅ Content calendar created!")

    # Display calendars
    if st.session_state.content_calendar:
        st.markdown("---")
        st.markdown("### 📆 Your Content Calendars")

        for idx, cal in enumerate(reversed(st.session_state.content_calendar)):
            # show selected date range if available
            if 'start_date' in cal and 'end_date' in cal:
                date_display = f" ({cal['start_date'].strftime('%b %d')} to {cal['end_date'].strftime('%b %d, %Y')})"
            else:
                date_display = f" - Week of {cal['timestamp'].strftime('%b %d, %Y')}"

            with st.expander(f"📅 {cal['topic']}{date_display}"):
                st.markdown("<div class='calendar-day'>", unsafe_allow_html=True)
                for platform in cal['platforms']:
                    st.markdown(get_platform_badge(platform), unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

                st.markdown(f"<div class='content-card'>{cal['calendar']}</div>", unsafe_allow_html=True)

                if st.button(f"📥 Export Calendar", key=f"export_{idx}"):
                    st.download_button(
                        "Download as Text",
                        cal['calendar'],
                        file_name=f"content_calendar_{cal['timestamp'].strftime('%Y%m%d')}.txt",
                        key=f"download_{idx}"
                    )

# =========================
# TAB 4: FULL PLAN
# =========================
with tab4:
    st.markdown("## 🚀 Generate Content Ideas, Daily Captions & Plans")
    st.info("💼 Create a complete content strategy with AI-powered ideas, captions, and planning!")

    # Plan Configuration
    col1, col2 = st.columns(2)

    with col1:
        num_days = st.slider(
            "Number of Days to Plan",
            min_value=1,
            max_value=30,
            value=7,
            step=1
        )

        primary_platform = st.selectbox(
            "Primary Platform",
            ["Instagram", "LinkedIn", "Twitter", "TikTok", "Facebook"],
            key="plan_platform"
        )

    with col2:
        content_focus = st.multiselect(
            "Content Focus Areas",
            ["Educational", "Entertaining", "Promotional", "Community", "Behind-the-Scenes", "Tips & Tricks"],
            default=["Educational", "Entertaining"],
            key="plan_focus"
        )

        posting_frequency = st.selectbox(
            "Daily Posting Frequency",
            ["1 post per day", "2 posts per day", "3+ posts per day"],
            key="posting_freq"
        )

    # Additional Parameters
    plan_topic = st.text_input(
        "Main Topic/Theme for the Week",
        placeholder="e.g., Product Launch, Holiday Campaign, Industry Tips...",
        key="plan_topic"
    )

    brand_voice = st.selectbox(
        "Brand Voice",
        ["Professional", "Casual", "Humorous", "Inspirational", "Technical"],
        key="plan_voice"
    )

    if st.button("🎯 Generate Full Content Plan", use_container_width=True, key="gen_plan_btn"):
        if st.session_state.api_key:
            with st.spinner("🤖 Generating your content plan..."):
                plan_prompt = f"""
Generate a comprehensive {num_days}-day social media content plan for {primary_platform}.

Requirements:
- Brand Voice: {brand_voice}
- Content Focus: {', '.join(content_focus)}
- Daily Posting Frequency: {posting_frequency}
- Main Topic: {plan_topic if plan_topic else 'General social media content'}

For each day, provide:
1. Content idea with brief description
2. Recommended caption (200-300 characters)
3. Hashtags (5-10 relevant)
4. Best posting time
5. Engagement tips

Format the output clearly with day numbers and sections.
"""

                plan_content = call_groq_api(
                    plan_prompt,
                    st.session_state.api_key,
                    max_tokens=4000,
                    temperature=0.7
                )

                if plan_content:
                    st.markdown("### 📋 Your Content Plan")
                    st.markdown(plan_content)

                    # Save to calendar-like storage
                    if st.button("💾 Save to Content Calendar", key="save_plan_btn"):
                        st.session_state.content_calendar.append({
                            'plan': plan_content,
                            'topic': plan_topic,
                            'days': num_days,
                            'platform': primary_platform,
                            'timestamp': datetime.now()
                        })
                        st.success("✅ Plan saved to Content Calendar!")

                    st.download_button(
                        "📥 Download Plan as Text",
                        plan_content,
                        file_name=f"content_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                        mime="text/plain",
                        key="download_plan_btn"
                    )
        else:
            st.warning("⚠️ Please enter your Groq API key in the sidebar first!")

    # Display saved plans
    if st.session_state.content_calendar:
        st.markdown("---")
        st.markdown("### 📚 Saved Content Plans")

        for idx, plan in enumerate(st.session_state.content_calendar):
            # Only show Tab 4 plan entries (those with 'plan' key)
            if 'plan' in plan and isinstance(plan.get('plan'), str):
                with st.expander(
                    f"📅 Plan {idx + 1} - {plan.get('topic', 'Untitled')} "
                    f"({plan.get('days', 'N/A')} days) - {plan['timestamp'].strftime('%Y-%m-%d')}"
                ):
                    st.markdown(plan['plan'])

                    col1b, col2b = st.columns(2)
                    with col1b:
                        st.download_button(
                            "📥 Download",
                            plan['plan'],
                            file_name=f"content_plan_{idx}_{plan['timestamp'].strftime('%Y%m%d')}.txt",
                            key=f"download_saved_plan_{idx}"
                        )
                    with col2b:
                        if st.button("🗑️ Delete", key=f"delete_plan_{idx}"):
                            st.session_state.content_calendar.pop(idx)
                            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>📱 <strong>Pro Tip:</strong> Save your generated content and mix AI-powered ideas with your own creativity!</p>
    <p style='font-size: 12px;'>Built with Streamlit & Groq API | Social Media Agent © 2025</p>
</div>
""", unsafe_allow_html=True)
