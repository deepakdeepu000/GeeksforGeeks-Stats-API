def generate_stats_svg(data: dict) -> str:
    user_name = data.get("userName", "User")
    total = data.get("totalProblemsSolved", 0)
    school = data.get("School", 0)
    basic = data.get("Basic", 0)
    easy = data.get("Easy", 0)
    medium = data.get("Medium", 0)
    hard = data.get("Hard", 0)
    profile_url = f"https://www.geeksforgeeks.org/profile/{user_name}?tab=activity"

    return f"""<svg width="380" height="220" viewBox="0 0 380 220" xmlns="http://www.w3.org/2000/svg">
<style>
svg {{ font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, 'Roboto', sans-serif; }}}}
#bg {{ fill: #0f1419; stroke: #1e2530; stroke-width: 1; rx: 12; ry: 12; }}
.header {{ font-size: 18px; font-weight: 700; fill: #f8f9fa; }}
.subheader {{ font-size: 13px; fill: #adb5bd; font-weight: 500; }}
.total {{ font-size: 36px; font-weight: 800; fill: url(#totalGrad); }}
.difficulty {{ font-size: 11px; fill: #adb5bd; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }}
.counts {{ font-size: 18px; font-weight: 700; fill: #fff; }}
.school {{ fill: #28a745 !important; }}
.basic {{ fill: #17a2b8 !important; }}
.easy {{ fill: #007bff !important; }}
.medium {{ fill: #ffc107 !important; color: #212529; }}
.hard {{ fill: #dc3545 !important; }}
.username {{ font-size: 12px; fill: #6c757d; font-weight: 500; }}
</style>

<defs>
  <linearGradient id="totalGrad" x1="0%" y1="0%" x2="100%" y2="100%">
    <stop offset="0%" stop-color="#00d4aa"/>
    <stop offset="50%" stop-color="#00a085"/>
    <stop offset="100%" stop-color="#00795e"/>
  </linearGradient>
  <pattern id="grain" width="4" height="4" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1" fill="#0f1419" opacity="0.1"/>
  </pattern>
</defs>

<g transform="translate(10,10)">
  <!-- Background -->
  <rect width="360" height="200" rx="12" ry="12" fill="url(#grain)" stroke="#1e2530" stroke-width="1"/>
  
  <!-- Gradient overlay -->
  <rect width="360" height="80" rx="12" ry="12" fill="url(#totalGrad)" opacity="0.1"/>
  
  <!-- Header -->
  <text x="25" y="28" class="header">GeeksforGeeks</text>
  <text x="25" y="45" class="subheader">Problems Solved</text>
  <text x="25" y="75" class="total">{total}</text>
  
  <!-- Username -->
  <a href="{profile_url}">
        <text x="25" y="105" class="username">@{user_name}</text>
    </a>
  
  <!-- Divider -->
  <rect x="20" y="115" width="320" height="1" rx="0.5" fill="#2c3e50" opacity="0.5"/>
  
  <!-- Difficulties Grid -->
 <g font-family="'Segoe UI', sans-serif" text-anchor="middle">
        <rect x="20" y="125" width="56" height="50" rx="6" fill="#ffffff"/>
        <text x="48" y="145" class="difficulty">School</text>
        <text x="48" y="167" class="counts school">{school}</text>
        
        <rect x="80" y="125" width="56" height="50" rx="6" fill="#ffffff"/>
        <text x="108" y="145" class="difficulty">Basic</text>
        <text x="108" y="167" class="counts basic">{basic}</text>
        
        <rect x="140" y="125" width="56" height="50" rx="6" fill="#ffffff"/>
        <text x="168" y="145" class="difficulty">Easy</text>
        <text x="168" y="167" class="counts easy">{easy}</text>
        
        <rect x="200" y="125" width="56" height="50" rx="6" fill="#ffffff"/>
        <text x="228" y="145" class="difficulty">Medium</text>
        <text x="228" y="167" class="counts medium">{medium}</text>
        
        <rect x="260" y="125" width="60" height="50" rx="6" fill="#ffffff"/>
        <text x="290" y="145" class="difficulty">Hard</text>
        <text x="290" y="167" class="counts hard">{hard}</text>
    </g>
  
  <!-- GFG Badge -->
  <g transform="translate(280, 18)">
    <rect width="70" height="20" rx="4" fill="#00c851" stroke="#00a843" stroke-width="0.5"/>
    <text x="35" y="15" font-size="11" font-weight="600" fill="#fff" text-anchor="middle">GFG</text>
  </g>
</g>
</svg>"""

