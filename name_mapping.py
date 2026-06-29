"""2026 FIFA World Cup teams, groups, and CSV name mapping.

`csv_name` is how the team appears in the historical results dataset; `name`
is the display name used everywhere in this app.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class WCTeam:
    csv_name: str
    name: str
    code: str
    group: str
    flag: str


WC2026_TEAMS: list[WCTeam] = [
    # Group A
    WCTeam("Mexico", "Mexico", "MEX", "A", "🇲🇽"),
    WCTeam("South Africa", "South Africa", "RSA", "A", "🇿🇦"),
    WCTeam("South Korea", "South Korea", "KOR", "A", "🇰🇷"),
    WCTeam("Czech Republic", "Czech Republic", "CZE", "A", "🇨🇿"),
    # Group B
    WCTeam("Canada", "Canada", "CAN", "B", "🇨🇦"),
    WCTeam("Bosnia and Herzegovina", "Bosnia & Herz.", "BIH", "B", "🇧🇦"),
    WCTeam("Qatar", "Qatar", "QAT", "B", "🇶🇦"),
    WCTeam("Switzerland", "Switzerland", "SUI", "B", "🇨🇭"),
    # Group C
    WCTeam("Brazil", "Brazil", "BRA", "C", "🇧🇷"),
    WCTeam("Morocco", "Morocco", "MAR", "C", "🇲🇦"),
    WCTeam("Haiti", "Haiti", "HAI", "C", "🇭🇹"),
    WCTeam("Scotland", "Scotland", "SCO", "C", "🏴󠁧󠁢󠁳󠁣󠁴U+E007F"),
    # Group D
    WCTeam("United States", "USA", "USA", "D", "🇺🇸"),
    WCTeam("Paraguay", "Paraguay", "PAR", "D", "🇵🇾"),
    WCTeam("Australia", "Australia", "AUS", "D", "🇦🇺"),
    WCTeam("Turkey", "Turkey", "TUR", "D", "🇹🇷"),
    # Group E
    WCTeam("Germany", "Germany", "GER", "E", "🇩🇪"),
    WCTeam("Curaçao", "Curaçao", "CUW", "E", "🇨🇼"),
    WCTeam("Ivory Coast", "Ivory Coast", "CIV", "E", "🇨🇮"),
    WCTeam("Ecuador", "Ecuador", "ECU", "E", "🇪🇨"),
    # Group F
    WCTeam("Netherlands", "Netherlands", "NED", "F", "🇳🇱"),
    WCTeam("Japan", "Japan", "JPN", "F", "🇯🇵"),
    WCTeam("Sweden", "Sweden", "SWE", "F", "🇸🇪"),
    WCTeam("Tunisia", "Tunisia", "TUN", "F", "🇹🇳"),
    # Group G
    WCTeam("Belgium", "Belgium", "BEL", "G", "🇧🇪"),
    WCTeam("Egypt", "Egypt", "EGY", "G", "🇪🇬"),
    WCTeam("Iran", "Iran", "IRN", "G", "🇮🇷"),
    WCTeam("New Zealand", "New Zealand", "NZL", "G", "🇳🇿"),
    # Group H
    WCTeam("Spain", "Spain", "ESP", "H", "🇪🇸"),
    WCTeam("Cape Verde", "Cape Verde", "CPV", "H", "🇨🇻"),
    WCTeam("Saudi Arabia", "Saudi Arabia", "KSA", "H", "🇸🇦"),
    WCTeam("Uruguay", "Uruguay", "URU", "H", "🇺🇾"),
    # Group I
    WCTeam("France", "France", "FRA", "I", "🇫🇷"),
    WCTeam("Senegal", "Senegal", "SEN", "I", "🇸🇳"),
    WCTeam("Iraq", "Iraq", "IRQ", "I", "🇮🇶"),
    WCTeam("Norway", "Norway", "NOR", "I", "🇳🇴"),
    # Group J
    WCTeam("Argentina", "Argentina", "ARG", "J", "🇦🇷"),
    WCTeam("Algeria", "Algeria", "ALG", "J", "🇩🇿"),
    WCTeam("Austria", "Austria", "AUT", "J", "🇦🇹"),
    WCTeam("Jordan", "Jordan", "JOR", "J", "🇯🇴"),
    # Group K
    WCTeam("Portugal", "Portugal", "POR", "K", "🇵🇹"),
    WCTeam("DR Congo", "DR Congo", "COD", "K", "🇨🇩"),
    WCTeam("Uzbekistan", "Uzbekistan", "UZB", "K", "🇺🇿"),
    WCTeam("Colombia", "Colombia", "COL", "K", "🇨🇴"),
    # Group L
    WCTeam("England", "England", "ENG", "L", "🏴󠁧󠁢󠁥󠁮󠁧U+E007F"),
    WCTeam("Croatia", "Croatia", "CRO", "L", "🇭🇷"),
    WCTeam("Ghana", "Ghana", "GHA", "L", "🇬🇭"),
    WCTeam("Panama", "Panama", "PAN", "L", "🇵🇦"),
]

GROUPS = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L"]


def find_team(query: str) -> WCTeam | None:
    """Match a team by display name or code, case-insensitively."""
    q = query.strip().lower()
    for t in WC2026_TEAMS:
        if t.name.lower() == q or t.code.lower() == q:
            return t
    # Fall back to a partial / prefix match on the display name.
    for t in WC2026_TEAMS:
        if q and (q in t.name.lower() or t.name.lower().startswith(q)):
            return t
    return None
