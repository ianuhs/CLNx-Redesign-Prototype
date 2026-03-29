import math
import sys
from datetime import datetime
from dataclasses import dataclass
from typing import Callable, List, Optional, Sequence, Tuple

import pygame


pygame.init()


WIDTH, HEIGHT = 1440, 900
FPS = 60

UOFT_BLUE = (30, 55, 101)

BG = (248, 250, 253)
PANEL = (255, 255, 255)
SOFT_PANEL = (244, 247, 252)
BORDER = (196, 206, 222)
TEXT = (31, 41, 55)
MUTED = (89, 104, 128)
ACCENT = (221, 231, 247)
ACCENT_DARK = UOFT_BLUE
ACCENT_LIGHT = (239, 244, 252)
BLUE_TINT = (230, 238, 250)
SIDEBAR = (247, 250, 255)
PLACEHOLDER = (224, 232, 243)
DANGER = (180, 63, 63)
SHADOW = (226, 233, 242)
TABLE_LINE = (0, 0, 0)
SEARCH_TABLE_WIDTHS = [324, 206, 116, 116, 116, 126]


FONT_UI = "arial"
FONT_SERIF = "timesnewroman"


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


def draw_text(
    surface: pygame.Surface,
    text: str,
    font: pygame.font.Font,
    color: Tuple[int, int, int],
    x: int,
    y: int,
    max_width: Optional[int] = None,
    line_spacing: int = 6,
) -> int:
    if max_width is None:
        rendered = font.render(text, True, color)
        surface.blit(rendered, (x, y))
        return rendered.get_height()

    words = text.split()
    if not words:
        return 0

    lines: List[str] = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if font.size(trial)[0] <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)

    height = 0
    for line in lines:
        rendered = font.render(line, True, color)
        surface.blit(rendered, (x, y + height))
        height += rendered.get_height() + line_spacing
    return height - line_spacing if lines else 0


def measure_text_height(
    text: str,
    font: pygame.font.Font,
    max_width: Optional[int] = None,
    line_spacing: int = 6,
) -> int:
    if max_width is None:
        return font.get_height()

    words = text.split()
    if not words:
        return 0

    lines = []
    current = words[0]
    for word in words[1:]:
        trial = f"{current} {word}"
        if font.size(trial)[0] <= max_width:
            current = trial
        else:
            lines.append(current)
            current = word
    lines.append(current)

    return len(lines) * font.get_height() + max(0, len(lines) - 1) * line_spacing


def dashed_rect(
    surface: pygame.Surface,
    rect: pygame.Rect,
    color: Tuple[int, int, int],
    dash: int = 10,
    gap: int = 6,
    width: int = 2,
) -> None:
    x1, y1, x2, y2 = rect.left, rect.top, rect.right, rect.bottom
    points = [
        ((x1, y1), (x2, y1)),
        ((x2, y1), (x2, y2)),
        ((x2, y2), (x1, y2)),
        ((x1, y2), (x1, y1)),
    ]
    for start, end in points:
        sx, sy = start
        ex, ey = end
        length = math.dist(start, end)
        dx = (ex - sx) / length if length else 0
        dy = (ey - sy) / length if length else 0
        progress = 0
        while progress < length:
            dash_end = min(progress + dash, length)
            p1 = (sx + dx * progress, sy + dy * progress)
            p2 = (sx + dx * dash_end, sy + dy * dash_end)
            pygame.draw.line(surface, color, p1, p2, width)
            progress += dash + gap


def make_font(size: int, bold: bool = False, serif: bool = False) -> pygame.font.Font:
    return pygame.font.SysFont(FONT_SERIF if serif else FONT_UI, size, bold=bold)


@dataclass
class JobPosting:
    title: str
    department: str
    position_type: str
    campus_location: str
    hours_per_week: str
    schedule_type: str
    contract_type: str
    start_date: str
    end_date: str
    positions: str
    location_details: str
    salary_type: str
    wage: str
    deadline: str
    summary: str
    responsibilities: List[str]
    qualifications: List[str]

    @property
    def table_type(self) -> str:
        return self.position_type

    @property
    def filter_blob(self) -> str:
        text_parts = [
            self.title,
            self.department,
            self.position_type,
            self.campus_location,
            self.schedule_type,
            self.summary,
            " ".join(self.responsibilities),
            " ".join(self.qualifications),
        ]
        return " ".join(text_parts).lower()

    @property
    def field_rows(self) -> List[Tuple[str, str]]:
        return [
            ("Contract or Permanent?", self.contract_type),
            ("Start Date", self.start_date),
            ("End Date", self.end_date),
            ("Number of Positions", self.positions),
            ("Campus Job Location", self.campus_location),
            ("Job Location Details", self.location_details),
            ("Annual Salary or Per Hour?", self.salary_type),
            ("Salary or Hourly Wage", self.wage),
            ("Hours Per Week", self.hours_per_week),
            ("Type of Schedule", self.schedule_type),
            (
                "Schedule Details",
                f"{self.hours_per_week} hours range, {self.schedule_type.lower()}",
            ),
            ("Department", self.department),
            ("Application Deadline", self.deadline),
        ]


def seed_jobs() -> List[JobPosting]:
    # Assumption: these roles are realistic placeholders for demoing the workflow.
    return [
        JobPosting(
            title="Library Services Assistant",
            department="Arts & Languages",
            position_type="Part Time",
            campus_location="U of T St. George",
            hours_per_week="11-24",
            schedule_type="Fixed Hours",
            contract_type="Contract",
            start_date="05/06/2026",
            end_date="08/28/2026",
            positions="2",
            location_details="E J Pratt Library, 71 Queen's Park Cres. East",
            salary_type="Per Hour",
            wage="$25 / hour",
            deadline="04/18/2026",
            summary="Support front-desk circulation, wayfinding, and light collection organization for a busy campus library.",
            responsibilities=[
                "Greet students and staff at the service desk.",
                "Assist with circulation, shelving, and basic equipment support.",
                "Help maintain a calm and accessible study environment.",
            ],
            qualifications=[
                "Strong communication and customer service skills.",
                "Comfort working in a fast-paced student-facing setting.",
                "Availability for weekday shifts during the summer term.",
            ],
        ),
        JobPosting(
            title="Engineering Outreach Program Coordinator",
            department="Engineering",
            position_type="Summer",
            campus_location="Tri-Campus",
            hours_per_week="25-34",
            schedule_type="Flexible Hours",
            contract_type="Contract",
            start_date="05/13/2026",
            end_date="09/03/2026",
            positions="1",
            location_details="Hybrid across outreach events at all three campuses",
            salary_type="Per Hour",
            wage="$28 / hour",
            deadline="04/14/2026",
            summary="Coordinate student-facing STEM outreach sessions, logistics, and communications across multiple campuses.",
            responsibilities=[
                "Schedule workshops and coordinate event materials.",
                "Support facilitator communications and participant registration lists.",
                "Track attendance and summarize engagement outcomes.",
            ],
            qualifications=[
                "Experience coordinating projects or events.",
                "Strong organization and writing skills.",
                "Interest in engineering outreach and student engagement.",
            ],
        ),
        JobPosting(
            title="IT Help Desk Assistant",
            department="Information Communication & Technology",
            position_type="Part Time",
            campus_location="U of T Mississauga",
            hours_per_week="11-24",
            schedule_type="Fixed Hours",
            contract_type="Contract",
            start_date="04/29/2026",
            end_date="12/18/2026",
            positions="3",
            location_details="Instructional Centre, UTM Campus",
            salary_type="Per Hour",
            wage="$24 / hour",
            deadline="04/11/2026",
            summary="Provide first-line technical support for student software, account, and classroom technology issues.",
            responsibilities=[
                "Troubleshoot common hardware and software issues.",
                "Document support tickets and escalate unresolved issues.",
                "Set up AV equipment for classes and events.",
            ],
            qualifications=[
                "Basic troubleshooting knowledge for Windows and macOS.",
                "Clear verbal communication skills.",
                "Able to work scheduled shifts on campus.",
            ],
        ),
        JobPosting(
            title="Research Data Assistant",
            department="Social Sciences",
            position_type="Full Time",
            campus_location="U of T Scarborough",
            hours_per_week="35+",
            schedule_type="Flexible Hours",
            contract_type="Contract",
            start_date="05/04/2026",
            end_date="08/31/2026",
            positions="1",
            location_details="Research suite, Department of Sociology, UTSC",
            salary_type="Per Hour",
            wage="$27 / hour",
            deadline="04/20/2026",
            summary="Clean, organize, and summarize qualitative and quantitative research data for a faculty-led summer project.",
            responsibilities=[
                "Prepare datasets and verify data quality.",
                "Assist with coding interview notes and research documentation.",
                "Create draft charts and short written summaries for the project team.",
            ],
            qualifications=[
                "Strong attention to detail.",
                "Comfort with spreadsheets or basic data tools.",
                "Interest in social research methods.",
            ],
        ),
        JobPosting(
            title="Student Wellness Program Assistant",
            department="Health & Life Sciences",
            position_type="Part Time",
            campus_location="U of T St. George",
            hours_per_week="1-10",
            schedule_type="Flexible Hours",
            contract_type="Contract",
            start_date="05/10/2026",
            end_date="11/27/2026",
            positions="2",
            location_details="Student Life wellness office, St. George campus",
            salary_type="Per Hour",
            wage="$23 / hour",
            deadline="04/22/2026",
            summary="Support wellness events, intake logistics, and student communications for peer-facing programming.",
            responsibilities=[
                "Prepare event materials and room setups.",
                "Respond to routine participant questions.",
                "Track attendance and support outreach campaigns.",
            ],
            qualifications=[
                "Empathetic communication style.",
                "Reliable organization and follow-through.",
                "Interest in student wellbeing programming.",
            ],
        ),
        JobPosting(
            title="Business Operations Assistant",
            department="Business",
            position_type="Full Time",
            campus_location="Off Campus",
            hours_per_week="35+",
            schedule_type="Fixed Hours",
            contract_type="Contract",
            start_date="05/01/2026",
            end_date="09/04/2026",
            positions="1",
            location_details="Partner organization office near downtown Toronto",
            salary_type="Per Hour",
            wage="$29 / hour",
            deadline="04/15/2026",
            summary="Assist with reporting, scheduling, and administrative coordination for a university partner organization.",
            responsibilities=[
                "Prepare meeting notes and workflow trackers.",
                "Support calendar coordination and reporting tasks.",
                "Assist with internal documentation and process updates.",
            ],
            qualifications=[
                "Comfort with spreadsheets and written communication.",
                "Strong administrative and organizational skills.",
                "Availability for regular weekday hours.",
            ],
        ),
        JobPosting(
            title="Kinesiology Lab Support Assistant",
            department="Kinesiology & Physical Education",
            position_type="Summer",
            campus_location="U of T St. George",
            hours_per_week="25-34",
            schedule_type="Fixed Hours",
            contract_type="Contract",
            start_date="05/07/2026",
            end_date="08/21/2026",
            positions="2",
            location_details="Goldring Centre laboratory spaces",
            salary_type="Per Hour",
            wage="$26 / hour",
            deadline="04/19/2026",
            summary="Prepare lab materials, support participant visits, and maintain accurate records for movement science studies.",
            responsibilities=[
                "Prepare equipment and check study rooms before sessions.",
                "Assist researchers during participant appointments.",
                "Maintain organized logs and consent form records.",
            ],
            qualifications=[
                "Detail-oriented and dependable.",
                "Comfort interacting with participants in a lab environment.",
                "Interest in kinesiology or human movement research.",
            ],
        ),
        JobPosting(
            title="MIE240 Teaching Assistant",
            department="Engineering",
            position_type="Part Time",
            campus_location="U of T St. George",
            hours_per_week="11-24",
            schedule_type="Fixed Hours",
            contract_type="Contract",
            start_date="09/07/2026",
            end_date="04/25/2027",
            positions="6",
            location_details="Myhal Centre",
            salary_type="Per Hour",
            wage="$50 / hour",
            deadline="04/19/2026",
            summary="Prepare tutorial materials, support student activites, and grade student submissions.",
            responsibilities=[
                "Prepare tutorial material and check classrooms before tutorials.",
                "Support human factors learning",
                "Grade and provide feedback for student submissions.",
            ],
            qualifications=[
                "Detail-oriented and dependable.",
                "Comfort interacting with students.",
                "Interest in human factors engineering.",
            ],
        ),
    ]


class Button:
    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        on_click: Callable[[], None],
        *,
        bg: Tuple[int, int, int] = PANEL,
        hover_bg: Tuple[int, int, int] = SOFT_PANEL,
        text_color: Tuple[int, int, int] = TEXT,
        border_color: Tuple[int, int, int] = BORDER,
        font: Optional[pygame.font.Font] = None,
        radius: int = 8,
    ) -> None:
        self.rect = rect
        self.label = label
        self.on_click = on_click
        self.bg = bg
        self.hover_bg = hover_bg
        self.text_color = text_color
        self.border_color = border_color
        self.font = font or make_font(20)
        self.radius = radius

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.on_click()
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        fill = self.hover_bg if hovered else self.bg
        pygame.draw.rect(surface, fill, self.rect, border_radius=self.radius)
        pygame.draw.rect(surface, self.border_color, self.rect, 1, border_radius=self.radius)
        rendered = self.font.render(self.label, True, self.text_color)
        surface.blit(rendered, rendered.get_rect(center=self.rect.center))


class TextInput:
    def __init__(self, rect: pygame.Rect, placeholder: str = "") -> None:
        self.rect = rect
        self.placeholder = placeholder
        self.value = ""
        self.active = False
        self.font = make_font(20)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            return self.active
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_ESCAPE:
                self.active = False
            elif event.unicode.isprintable():
                self.value += event.unicode
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        fill = PANEL
        border = ACCENT_DARK if self.active else BORDER
        pygame.draw.rect(surface, fill, self.rect, border_radius=6)
        pygame.draw.rect(surface, border, self.rect, 2 if self.active else 1, border_radius=6)
        display = self.value if self.value else self.placeholder
        color = TEXT if self.value else MUTED
        rendered = self.font.render(display, True, color)
        surface.blit(rendered, (self.rect.x + 14, self.rect.y + 12))
        if self.active:
            cursor_x = self.rect.x + 14 + rendered.get_width() + 2
            pygame.draw.line(
                surface,
                ACCENT_DARK,
                (cursor_x, self.rect.y + 10),
                (cursor_x, self.rect.y + self.rect.height - 10),
                2,
            )


class Dropdown:
    OPEN_MENU: Optional["Dropdown"] = None

    def __init__(
        self,
        rect: pygame.Rect,
        label: str,
        options: Sequence[str],
        default: str = "Any",
    ) -> None:
        self.rect = rect
        self.label = label
        self.options = [default] + list(options)
        self.selected = default
        self.font = make_font(18)
        self.option_height = 36
        self.max_menu_height = 252
        self.menu_scroll = 0

    @property
    def menu_rect(self) -> pygame.Rect:
        height = min(self.option_height * len(self.options), self.max_menu_height)
        y = self.rect.bottom + 2
        if y + height > HEIGHT - 60:
            y = self.rect.top - height - 2
        return pygame.Rect(self.rect.x, y, self.rect.width, height)

    @property
    def max_scroll(self) -> int:
        return max(0, self.option_height * len(self.options) - self.menu_rect.height)

    def handle_event(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                Dropdown.OPEN_MENU = None if Dropdown.OPEN_MENU is self else self
                return True
            if Dropdown.OPEN_MENU is self and self.menu_rect.collidepoint(event.pos):
                relative_y = event.pos[1] - self.menu_rect.y + self.menu_scroll
                index = int(relative_y // self.option_height)
                if 0 <= index < len(self.options):
                    self.selected = self.options[index]
                Dropdown.OPEN_MENU = None
                return True
            if Dropdown.OPEN_MENU is self:
                Dropdown.OPEN_MENU = None
        if event.type == pygame.MOUSEWHEEL and Dropdown.OPEN_MENU is self:
            if self.menu_rect.collidepoint(pygame.mouse.get_pos()):
                self.menu_scroll = int(clamp(self.menu_scroll - event.y * 28, 0, self.max_scroll))
                return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        label_font = make_font(16, bold=True)
        label_text = label_font.render(self.label, True, MUTED)
        surface.blit(label_text, (self.rect.x, self.rect.y - 22))

        pygame.draw.rect(surface, PANEL, self.rect, border_radius=6)
        pygame.draw.rect(surface, BORDER, self.rect, 1, border_radius=6)
        selected_text = self.font.render(self.selected, True, TEXT)
        surface.blit(selected_text, (self.rect.x + 12, self.rect.y + 10))
        arrow = "▲" if Dropdown.OPEN_MENU is self else "▼"
        arrow_text = self.font.render(arrow, True, MUTED)
        surface.blit(
            arrow_text,
            (self.rect.right - arrow_text.get_width() - 12, self.rect.y + 10),
        )

    def draw_menu(self, surface: pygame.Surface) -> None:
        if Dropdown.OPEN_MENU is not self:
            return

        menu = self.menu_rect
        shadow = menu.inflate(10, 10)
        pygame.draw.rect(surface, (226, 234, 244), shadow, border_radius=8)
        pygame.draw.rect(surface, PANEL, menu, border_radius=6)
        pygame.draw.rect(surface, BORDER, menu, 1, border_radius=6)

        clip_before = surface.get_clip()
        surface.set_clip(menu)
        for idx, option in enumerate(self.options):
            row = pygame.Rect(menu.x, menu.y + idx * self.option_height - self.menu_scroll, menu.width, self.option_height)
            hovered = row.collidepoint(pygame.mouse.get_pos())
            if option == self.selected:
                pygame.draw.rect(surface, ACCENT_LIGHT, row)
            elif hovered:
                pygame.draw.rect(surface, SOFT_PANEL, row)
            text = self.font.render(option, True, TEXT)
            surface.blit(text, (row.x + 12, row.y + 8))
        surface.set_clip(clip_before)

        if self.max_scroll > 0:
            bar_height = max(40, int(menu.height * (menu.height / (self.option_height * len(self.options)))))
            bar_y = menu.y + int((self.menu_scroll / self.max_scroll) * (menu.height - bar_height))
            pygame.draw.rect(surface, PLACEHOLDER, pygame.Rect(menu.right - 8, menu.y + 4, 4, menu.height - 8), border_radius=3)
            pygame.draw.rect(surface, ACCENT_DARK, pygame.Rect(menu.right - 8, bar_y + 4, 4, bar_height - 8), border_radius=3)


class ScrollState:
    def __init__(self) -> None:
        self.offset = 0

    def update(self, delta: int, view_height: int, content_height: int) -> None:
        max_offset = max(0, content_height - view_height)
        self.offset = int(clamp(self.offset + delta, 0, max_offset))

    def set_bounds(self, view_height: int, content_height: int) -> None:
        max_offset = max(0, content_height - view_height)
        self.offset = int(clamp(self.offset, 0, max_offset))


class AppState:
    def __init__(self) -> None:
        self.screen = "login"
        self.jobs = seed_jobs()
        self.selected_job: Optional[JobPosting] = None
        self.search_input = TextInput(pygame.Rect(324, 236, 420, 48), "")
        self.filter_panel_open = False
        self.results_scroll = ScrollState()
        self.details_scroll = ScrollState()
        self.apply_scroll = ScrollState()
        self.top_nav_items = [
            ("Overview", False),
            ("Jobs & Recruitment", True),
            ("Experiential Learning", False),
            ("Programs", False),
            ("My Board", False),
            ("Student Resources", False),
            ("Logout", False),
        ]
        self.left_nav_items = [
            ("Jobs & Recruitment", True, False),
            ("On-Campus Jobs", True, True),
            ("Off-Campus Jobs", False, False),
            ("Work Study", False, False),
            ("Volunteer Roles", False, False),
            ("My Applications", False, False),
            ("Shortlisted", False, False),
        ]

        self.filter_defs: List[Tuple[str, List[str]]] = [
            ("Position Type", ["Part Time", "Full Time", "Summer"]),
            (
                "Campus Location",
                [
                    "U of T Mississauga",
                    "U of T St. George",
                    "U of T Scarborough",
                    "Tri-Campus",
                    "Off Campus",
                ],
            ),
            ("Hours per Week", ["1-10", "11-24", "25-34", "35+"]),
            (
                "Department",
                [
                    "Actuarial Science",
                    "Architecture",
                    "Arts & Languages",
                    "Business",
                    "Computer & Math Sciences",
                    "Dentistry",
                    "Education",
                    "Engineering",
                    "Forestry",
                    "Health & Life Sciences",
                    "Human Resources & Industrial Relations",
                    "Information Communication & Technology",
                    "Kinesiology & Physical Education",
                    "Law",
                    "Medicine",
                    "Nursing",
                    "Pharmacy",
                    "Physical Sciences",
                    "Physiotherapy/Occupational Therapy",
                    "Social Sciences",
                    "Social Work",
                ],
            ),
            ("Type of Schedule", ["Fixed Hours", "Flexible Hours"]),
            ("Sort by Deadline", ["Earliest First", "Latest First"]),
        ]
        self.dropdowns: List[Dropdown] = []
        self._build_dropdowns()

    def _build_dropdowns(self) -> None:
        self.dropdowns.clear()
        positions = [
            pygame.Rect(324, 330, 240, 44),
            pygame.Rect(588, 330, 300, 44),
            pygame.Rect(912, 330, 240, 44),
            pygame.Rect(324, 402, 564, 44),
            pygame.Rect(912, 402, 240, 44),
            pygame.Rect(324, 474, 240, 44),
        ]
        for idx, ((label, options), rect) in enumerate(zip(self.filter_defs, positions)):
            default = "Any"
            dropdown = Dropdown(rect, label, options, default=default)
            if idx == 3:
                dropdown.selected = "Any"
            self.dropdowns.append(dropdown)

    def reset_filters(self) -> None:
        self.search_input.value = ""
        for dropdown in self.dropdowns:
            dropdown.selected = "Any"
        self.results_scroll.offset = 0

    def filtered_jobs(self) -> List[JobPosting]:
        query = self.search_input.value.strip().lower()
        results: List[JobPosting] = []
        sort_value = "Any"

        for dropdown in self.dropdowns:
            if dropdown.label == "Sort by Deadline":
                sort_value = dropdown.selected
                break

        for job in self.jobs:
            if query and query not in job.filter_blob:
                continue

            selected_map = {
                "Position Type": job.position_type,
                "Campus Location": job.campus_location,
                "Hours per Week": job.hours_per_week,
                "Department": job.department,
                "Type of Schedule": job.schedule_type,
            }
            include = True
            for dropdown in self.dropdowns:
                if dropdown.label == "Sort by Deadline":
                    continue
                if dropdown.selected != "Any" and selected_map[dropdown.label] != dropdown.selected:
                    include = False
                    break
            if include:
                results.append(job)

        if sort_value != "Any":
            reverse = sort_value == "Latest First"
            results.sort(key=lambda job: datetime.strptime(job.deadline, "%m/%d/%Y"), reverse=reverse)

        return results


def draw_window_chrome(surface: pygame.Surface) -> None:
    surface.fill(BG)
    pygame.draw.rect(surface, PANEL, pygame.Rect(24, 24, WIDTH - 48, HEIGHT - 48), border_radius=18)
    pygame.draw.rect(surface, SHADOW, pygame.Rect(24, 24, WIDTH - 48, HEIGHT - 48), 1, border_radius=18)


def draw_login_page(surface: pygame.Surface, login_button: Button) -> None:
    draw_window_chrome(surface)
    hero = pygame.Rect(120, 140, WIDTH - 240, HEIGHT - 280)
    pygame.draw.rect(surface, SOFT_PANEL, hero, border_radius=24)
    pygame.draw.rect(surface, BORDER, hero, 1, border_radius=24)

    eyebrow = make_font(18, bold=True)
    title = make_font(48, bold=True, serif=True)
    body = make_font(24)

    surface.blit(eyebrow.render("CLNx Prototype", True, ACCENT_DARK), (hero.x + 70, hero.y + 80))
    draw_text(
        surface,
        "A simplified login entry for the redesigned on-campus job journey.",
        title,
        TEXT,
        hero.x + 70,
        hero.y + 130,
        max_width=760,
        line_spacing=10,
    )
    draw_text(
        surface,
        "This screen intentionally skips verification so testers can move directly into the prototype experience and evaluate the search-to-apply flow.",
        body,
        MUTED,
        hero.x + 70,
        hero.y + 270,
        max_width=700,
        line_spacing=10,
    )

    
    login_button.draw(surface)


def draw_top_nav(surface: pygame.Surface, state: AppState) -> None:
    top_bar = pygame.Rect(80, 70, WIDTH - 160, 72)
    pygame.draw.rect(surface, PANEL, top_bar)
    pygame.draw.line(surface, BORDER, (top_bar.left, top_bar.bottom), (top_bar.right, top_bar.bottom), 1)

    x = top_bar.x + 18
    for label, active in state.top_nav_items:
        pill_pad = 14 if active else 10
        font = make_font(20, bold=active)
        text = font.render(label, True, ACCENT_DARK if active else MUTED)
        if active:
            pill = pygame.Rect(x - pill_pad, top_bar.y + 17, text.get_width() + pill_pad * 2, 38)
            pygame.draw.rect(surface, ACCENT, pill, border_radius=16)
            pygame.draw.rect(surface, BORDER, pill, 1, border_radius=16)
        surface.blit(text, (x, top_bar.y + 24))
        x += text.get_width() + 42


def draw_left_nav(surface: pygame.Surface, state: AppState) -> None:
    sidebar = pygame.Rect(80, 142, 230, HEIGHT - 220)
    pygame.draw.rect(surface, SIDEBAR, sidebar)
    pygame.draw.rect(surface, BORDER, sidebar, 1)
    y = sidebar.y + 18
    for label, interactive, active in state.left_nav_items:
        font = make_font(18, bold=interactive)
        color = ACCENT_DARK if active else (TEXT if interactive else MUTED)
        text = font.render(label, True, color)
        if active:
            pill_width = min(text.get_width() + 26, sidebar.width - 28)
            pill = pygame.Rect(sidebar.x + 14, y - 6, pill_width, 34)
            pygame.draw.rect(surface, ACCENT, pill, border_radius=14)
        surface.blit(text, (sidebar.x + 14, y))
        y += 46 if label == "Jobs & Recruitment" else 34


def get_main_content_rect() -> pygame.Rect:
    return pygame.Rect(310, 142, WIDTH - 390, HEIGHT - 220)


def draw_shell(surface: pygame.Surface, state: AppState) -> pygame.Rect:
    draw_window_chrome(surface)
    draw_top_nav(surface, state)
    draw_left_nav(surface, state)
    content = get_main_content_rect()
    pygame.draw.rect(surface, PANEL, content)
    pygame.draw.rect(surface, BORDER, content, 1)
    return content


def get_search_list_view_height(filter_panel_open: bool) -> int:
    content = get_main_content_rect()
    table_top = content.y + (428 if filter_panel_open else 170)
    header_bottom = table_top + 42
    return content.bottom - header_bottom - 28


def get_search_row_height(job: JobPosting, widths: List[int]) -> int:
    cells = [job.title, job.department, job.table_type, job.wage, job.deadline]
    heights = [
        measure_text_height(cell, make_font(16), width - 20, 4)
        for cell, width in zip(cells, widths)
    ]
    return max(76, max(heights) + 28)


def get_search_content_height(jobs: List[JobPosting], widths: List[int], view_height: int) -> int:
    total = sum(get_search_row_height(job, widths) for job in jobs)
    return max(total, view_height)


def get_details_content_height(job: JobPosting, viewport_width: int) -> int:
    row_h = 46
    section_y = 320 + len(job.field_rows) * row_h + 40
    y = section_y + 34
    bullet_width = viewport_width - 24

    for item in job.responsibilities:
        item_height = measure_text_height(item, make_font(18), bullet_width, 6)
        y += max(36, item_height + 10)

    y += 44
    for item in job.qualifications:
        item_height = measure_text_height(item, make_font(18), bullet_width, 6)
        y += max(36, item_height + 10)

    return y + 22 + 46 + 24


def draw_search_page(
    surface: pygame.Surface,
    state: AppState,
    search_button: Button,
    filters_button: Button,
    reset_button: Button,
    result_buttons: List[Button],
) -> None:
    content = draw_shell(surface, state)
    jobs = state.filtered_jobs()
    search_y = content.y + 94
    state.search_input.rect = pygame.Rect(content.x + 24, search_y, 430, 48)
    search_button.rect = pygame.Rect(state.search_input.rect.right + 18, search_y, 122, 48)
    filters_button.rect = pygame.Rect(search_button.rect.right + 18, search_y, 134, 48)

    title_font = make_font(28, bold=True)
    subtitle_font = make_font(18)
    surface.blit(title_font.render("On-Campus Jobs", True, TEXT), (content.x + 24, content.y + 20))
    draw_text(
        surface,
        "Search and refine on-campus roles using keywords and focused filters.",
        subtitle_font,
        MUTED,
        content.x + 24,
        content.y + 58,
        max_width=780,
    )

    state.search_input.draw(surface)
    search_button.draw(surface)
    filters_button.draw(surface)

    if state.filter_panel_open:
        panel = pygame.Rect(content.x + 24, content.y + 156, content.width - 48, 248)
        pygame.draw.rect(surface, SOFT_PANEL, panel, border_radius=12)
        pygame.draw.rect(surface, BORDER, panel, 1, border_radius=12)
        filter_positions = [
            pygame.Rect(panel.x + 24, panel.y + 38, 240, 44),
            pygame.Rect(panel.x + 288, panel.y + 38, 300, 44),
            pygame.Rect(panel.x + 612, panel.y + 38, 240, 44),
            pygame.Rect(panel.x + 24, panel.y + 110, 564, 44),
            pygame.Rect(panel.x + 612, panel.y + 110, 240, 44),
            pygame.Rect(panel.x + 24, panel.y + 182, 240, 44),
        ]
        for dropdown, rect in zip(state.dropdowns, filter_positions):
            dropdown.rect = rect
        for dropdown in state.dropdowns:
            dropdown.draw(surface)
        reset_button.rect = pygame.Rect(panel.right - 164, panel.y + 182, 140, 44)
        reset_button.draw(surface)

    table_top = content.y + (428 if state.filter_panel_open else 170)
    headers = ["Job Title", "Department", "Type", "Wage", "Deadline", "Action"]
    widths = SEARCH_TABLE_WIDTHS[:]
    header_rect = pygame.Rect(content.x + 24, table_top, sum(widths), 42)
    pygame.draw.rect(surface, SOFT_PANEL, header_rect)
    pygame.draw.rect(surface, TABLE_LINE, header_rect, 1)

    x = header_rect.x
    for header, width in zip(headers, widths):
        pygame.draw.line(surface, TABLE_LINE, (x, header_rect.y), (x, header_rect.bottom), 1)
        surface.blit(make_font(16, bold=True).render(header, True, MUTED), (x + 12, header_rect.y + 11))
        x += width
    pygame.draw.line(surface, TABLE_LINE, (header_rect.right, header_rect.y), (header_rect.right, header_rect.bottom), 1)

    list_rect = pygame.Rect(header_rect.x, header_rect.bottom, header_rect.width, content.bottom - header_rect.bottom - 28)
    pygame.draw.rect(surface, PANEL, list_rect)
    pygame.draw.rect(surface, TABLE_LINE, list_rect, 1)

    row_heights = [get_search_row_height(job, widths) for job in jobs]
    content_height = max(sum(row_heights), list_rect.height)
    state.results_scroll.set_bounds(list_rect.height, content_height)

    clip_before = surface.get_clip()
    surface.set_clip(list_rect)

    result_buttons.clear()
    y = list_rect.y - state.results_scroll.offset
    for idx, job in enumerate(jobs):
        row_height = row_heights[idx]
        row = pygame.Rect(list_rect.x, y, list_rect.width, row_height)
        pygame.draw.rect(surface, PANEL, row)
        pygame.draw.line(surface, TABLE_LINE, (row.x, row.y), (row.right, row.y), 1)
        pygame.draw.line(surface, TABLE_LINE, (row.x, row.bottom), (row.right, row.bottom), 1)

        cells = [
            (job.title, widths[0]),
            (job.department, widths[1]),
            (job.table_type, widths[2]),
            (job.wage, widths[3]),
            (job.deadline, widths[4]),
        ]
        cell_x = row.x
        for text, width in cells:
            draw_text(surface, text, make_font(16), TEXT, cell_x + 12, row.y + 14, max_width=width - 20, line_spacing=4)
            pygame.draw.line(surface, TABLE_LINE, (cell_x, row.y), (cell_x, row.bottom), 1)
            cell_x += width

        pygame.draw.line(surface, TABLE_LINE, (cell_x, row.y), (cell_x, row.bottom), 1)
        button_rect = pygame.Rect(cell_x + 14, row.y + max(18, (row_height - 40) // 2), widths[-1] - 28, 40)
        btn = Button(
            button_rect,
            "Apply/View",
            on_click=lambda posting=job: open_job_details(state, posting),
            bg=ACCENT_LIGHT,
            hover_bg=ACCENT,
            text_color=ACCENT_DARK,
            border_color=BORDER,
            font=make_font(16, bold=True),
        )
        btn.draw(surface)
        result_buttons.append(btn)
        pygame.draw.line(surface, TABLE_LINE, (cell_x + widths[-1], row.y), (cell_x + widths[-1], row.bottom), 1)
        y += row_height

    if not jobs:
        draw_text(
            surface,
            "No postings match the current search and filters.",
            make_font(20, bold=True),
            MUTED,
            list_rect.x + 24,
            list_rect.y + 24,
        )
        draw_text(
            surface,
            "Try broadening the search term or resetting the filter selections.",
            make_font(18),
            MUTED,
            list_rect.x + 24,
            list_rect.y + 58,
        )

    surface.set_clip(clip_before)
    if state.filter_panel_open and Dropdown.OPEN_MENU is not None:
        Dropdown.OPEN_MENU.draw_menu(surface)

    if content_height > list_rect.height:
        bar_height = max(48, int(list_rect.height * (list_rect.height / content_height)))
        max_scroll = content_height - list_rect.height
        bar_y = list_rect.y + int((state.results_scroll.offset / max_scroll) * (list_rect.height - bar_height))
        pygame.draw.rect(surface, PLACEHOLDER, pygame.Rect(list_rect.right + 8, list_rect.y, 8, list_rect.height), border_radius=4)
        pygame.draw.rect(surface, ACCENT, pygame.Rect(list_rect.right + 8, bar_y, 8, bar_height), border_radius=4)

    footer_text = f"{len(jobs)} job posting{'s' if len(jobs) != 1 else ''} shown"
    surface.blit(make_font(16).render(footer_text, True, MUTED), (list_rect.x, list_rect.bottom + 10))


def draw_back_button(surface: pygame.Surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(surface, PANEL, rect, border_radius=8)
    pygame.draw.rect(surface, BORDER, rect, 1, border_radius=8)
    label = make_font(18, bold=True).render("Back", True, TEXT)
    surface.blit(label, label.get_rect(center=rect.center))


def draw_details_page(
    surface: pygame.Surface,
    state: AppState,
    back_button: Button,
    apply_top_button: Button,
    apply_bottom_button: Button,
) -> None:
    content = draw_shell(surface, state)
    job = state.selected_job
    if job is None:
        return

    viewport = pygame.Rect(content.x + 24, content.y + 22, content.width - 48, content.height - 44)
    content_height = get_details_content_height(job, viewport.width)
    state.details_scroll.set_bounds(viewport.height, content_height)

    clip_before = surface.get_clip()
    surface.set_clip(viewport)
    base_y = viewport.y - state.details_scroll.offset

    back_button.rect.topleft = (viewport.x, base_y)
    back_button.draw(surface)

    breadcrumb = make_font(16).render("On-Campus Jobs / Details", True, MUTED)
    surface.blit(breadcrumb, (viewport.x + 110, base_y + 12))

    title_font = make_font(38, bold=True, serif=True)
    surface.blit(title_font.render(job.title, True, TEXT), (viewport.x, base_y + 70))
    surface.blit(make_font(20).render(job.department, True, MUTED), (viewport.x, base_y + 126))

    apply_top_button.rect.topleft = (viewport.right - 180, base_y + 68)
    apply_top_button.draw(surface)

    summary_card = pygame.Rect(viewport.x, base_y + 172, viewport.width, 120)
    pygame.draw.rect(surface, SOFT_PANEL, summary_card, border_radius=10)
    pygame.draw.rect(surface, BORDER, summary_card, 1, border_radius=10)
    surface.blit(make_font(18, bold=True).render("Position Summary", True, TEXT), (summary_card.x + 18, summary_card.y + 16))
    draw_text(surface, job.summary, make_font(20), TEXT, summary_card.x + 18, summary_card.y + 46, max_width=summary_card.width - 36, line_spacing=8)

    table_x = viewport.x
    table_y = base_y + 320
    left_w = 330
    right_w = viewport.width - left_w
    row_h = 46
    for idx, (label, value) in enumerate(job.field_rows):
        row = pygame.Rect(table_x, table_y + idx * row_h, viewport.width, row_h)
        fill = PANEL if idx % 2 == 0 else (251, 252, 250)
        pygame.draw.rect(surface, fill, row)
        pygame.draw.rect(surface, BORDER, row, 1)
        pygame.draw.line(surface, BORDER, (table_x + left_w, row.y), (table_x + left_w, row.bottom), 1)
        draw_text(surface, label + ":", make_font(18, bold=True), TEXT, row.x + 12, row.y + 12, max_width=left_w - 24, line_spacing=4)
        draw_text(surface, value, make_font(18), TEXT, row.x + left_w + 12, row.y + 12, max_width=right_w - 24, line_spacing=4)

    section_y = table_y + len(job.field_rows) * row_h + 40
    surface.blit(make_font(20, bold=True).render("Responsibilities", True, TEXT), (viewport.x, section_y))
    y = section_y + 34
    for item in job.responsibilities:
        pygame.draw.circle(surface, ACCENT_DARK, (viewport.x + 9, y + 11), 4)
        item_height = draw_text(surface, item, make_font(18), TEXT, viewport.x + 24, y, max_width=viewport.width - 24)
        y += max(36, item_height + 10)

    surface.blit(make_font(20, bold=True).render("Qualifications", True, TEXT), (viewport.x, y + 10))
    y += 44
    for item in job.qualifications:
        pygame.draw.circle(surface, ACCENT_DARK, (viewport.x + 9, y + 11), 4)
        item_height = draw_text(surface, item, make_font(18), TEXT, viewport.x + 24, y, max_width=viewport.width - 24)
        y += max(36, item_height + 10)

    apply_bottom_button.rect = pygame.Rect(viewport.x, y + 22, viewport.width, 46)
    apply_bottom_button.draw(surface)

    surface.set_clip(clip_before)

    if content_height > viewport.height:
        bar_height = max(60, int(viewport.height * (viewport.height / content_height)))
        max_scroll = content_height - viewport.height
        bar_y = viewport.y + int((state.details_scroll.offset / max_scroll) * (viewport.height - bar_height))
        pygame.draw.rect(surface, PLACEHOLDER, pygame.Rect(viewport.right + 8, viewport.y, 8, viewport.height), border_radius=4)
        pygame.draw.rect(surface, ACCENT, pygame.Rect(viewport.right + 8, bar_y, 8, bar_height), border_radius=4)


def draw_apply_page(surface: pygame.Surface, state: AppState, back_button: Button) -> None:
    content = draw_shell(surface, state)
    job = state.selected_job
    if job is None:
        return

    viewport = pygame.Rect(content.x + 24, content.y + 22, content.width - 48, content.height - 44)
    content_height = 980
    state.apply_scroll.set_bounds(viewport.height, content_height)

    clip_before = surface.get_clip()
    surface.set_clip(viewport)
    base_y = viewport.y - state.apply_scroll.offset

    back_button.rect.topleft = (viewport.x, base_y)
    back_button.draw(surface)

    title = make_font(36, bold=True, serif=True)
    surface.blit(title.render("Application", True, TEXT), (viewport.x + 110, base_y + 4))
    surface.blit(make_font(20).render(job.title, True, MUTED), (viewport.x + 110, base_y + 50))

    progress_y = base_y + 104
    steps = [("Job Search", True), ("Job Details", True), ("Upload Documents", True), ("Review", False), ("Submit", False)]
    x = viewport.x
    for idx, (label, complete) in enumerate(steps):
        step_rect = pygame.Rect(x, progress_y, 186, 36)
        fill = ACCENT if idx < 3 else SOFT_PANEL
        text_color = ACCENT_DARK if idx < 3 else MUTED
        pygame.draw.rect(surface, fill, step_rect, border_radius=8)
        pygame.draw.rect(surface, BORDER, step_rect, 1, border_radius=8)
        surface.blit(make_font(16, bold=True).render(label, True, text_color), (step_rect.x + 14, step_rect.y + 9))
        x += 196

    callout = pygame.Rect(viewport.x, base_y + 162, viewport.width, 84)
    pygame.draw.rect(surface, SOFT_PANEL, callout, border_radius=10)
    pygame.draw.rect(surface, BORDER, callout, 1, border_radius=10)
    draw_text(
        surface,
        "Upload the required documents for this posting.",
        make_font(19),
        TEXT,
        callout.x + 18,
        callout.y + 18,
        max_width=callout.width - 36,
        line_spacing=8,
    )

    form_y = base_y + 274
    labels = [
        ("Cover Letter", True),
        ("Resume / CV", True),
        ("Other (Optional)", False),
    ]
    for idx, (label, required) in enumerate(labels):
        y = form_y + idx * 180
        label_text = f"{label} {'*' if required else ''}"
        label_font = make_font(22, bold=True)
        surface.blit(label_font.render(label_text, True, DANGER if required else TEXT), (viewport.x, y))
        drop_rect = pygame.Rect(viewport.x, y + 34, viewport.width, 112)
        dashed_rect(surface, drop_rect, BORDER)
        helper = "Drag files here or browse"
        helper_render = make_font(20).render(helper, True, MUTED)
        surface.blit(helper_render, helper_render.get_rect(center=drop_rect.center))
        browse_rect = pygame.Rect(drop_rect.centerx - 62, drop_rect.centery + 26, 124, 34)
        pygame.draw.rect(surface, PANEL, browse_rect, border_radius=8)
        pygame.draw.rect(surface, BORDER, browse_rect, 1, border_radius=8)
        browse_text = make_font(16, bold=True).render("Browse", True, TEXT)
        surface.blit(browse_text, browse_text.get_rect(center=browse_rect.center))

    notes_y = form_y + 560
    surface.blit(make_font(20, bold=True).render("Application Notes", True, TEXT), (viewport.x, notes_y))
    notes_rect = pygame.Rect(viewport.x, notes_y + 36, viewport.width, 130)
    pygame.draw.rect(surface, PANEL, notes_rect, border_radius=10)
    pygame.draw.rect(surface, BORDER, notes_rect, 1, border_radius=10)
    draw_text(
        surface,
        "This prototype ends on the upload page by design. A production workflow would continue into review and submission confirmation.",
        make_font(18),
        MUTED,
        notes_rect.x + 18,
        notes_rect.y + 18,
        max_width=notes_rect.width - 36,
        line_spacing=8,
    )

    surface.set_clip(clip_before)

    if content_height > viewport.height:
        bar_height = max(60, int(viewport.height * (viewport.height / content_height)))
        max_scroll = content_height - viewport.height
        bar_y = viewport.y + int((state.apply_scroll.offset / max_scroll) * (viewport.height - bar_height))
        pygame.draw.rect(surface, PLACEHOLDER, pygame.Rect(viewport.right + 8, viewport.y, 8, viewport.height), border_radius=4)
        pygame.draw.rect(surface, ACCENT, pygame.Rect(viewport.right + 8, bar_y, 8, bar_height), border_radius=4)


def open_job_details(state: AppState, job: JobPosting) -> None:
    state.selected_job = job
    state.screen = "details"
    state.details_scroll.offset = 0
    Dropdown.OPEN_MENU = None


def open_application(state: AppState) -> None:
    state.screen = "apply"
    state.apply_scroll.offset = 0


def go_back_to_search(state: AppState) -> None:
    state.screen = "search"
    Dropdown.OPEN_MENU = None


def go_back_to_details(state: AppState) -> None:
    state.screen = "details"


def main() -> None:
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("CLNx Job Flow Prototype")
    clock = pygame.time.Clock()
    state = AppState()

    login_button = Button(
        pygame.Rect(190, 600, 220, 56),
        "Log In",
        on_click=lambda: setattr(state, "screen", "search"),
        bg=ACCENT,
        hover_bg=(184, 221, 196),
        text_color=ACCENT_DARK,
        border_color=BORDER,
        font=make_font(22, bold=True),
        radius=12,
    )
    search_button = Button(
        pygame.Rect(772, 236, 122, 48),
        "Search",
        on_click=lambda: None,
        bg=ACCENT_DARK,
        hover_bg=(42, 74, 130),
        text_color=PANEL,
        border_color=ACCENT_DARK,
        font=make_font(18, bold=True),
    )
    filters_button = Button(
        pygame.Rect(912, 236, 134, 48),
        "Filters",
        on_click=lambda: setattr(state, "filter_panel_open", not state.filter_panel_open),
        bg=PANEL,
        hover_bg=ACCENT_LIGHT,
        border_color=ACCENT_DARK,
        font=make_font(18, bold=True),
    )
    reset_button = Button(
        pygame.Rect(1046, 402, 140, 44),
        "Reset Filters",
        on_click=state.reset_filters,
        bg=PANEL,
        hover_bg=ACCENT_LIGHT,
        border_color=ACCENT_DARK,
        font=make_font(16, bold=True),
    )
    details_back_button = Button(
        pygame.Rect(0, 0, 88, 40),
        "Back",
        on_click=lambda: go_back_to_search(state),
        bg=PANEL,
        hover_bg=ACCENT_LIGHT,
        border_color=ACCENT_DARK,
        font=make_font(18, bold=True),
    )
    details_apply_top = Button(
        pygame.Rect(0, 0, 160, 46),
        "Apply Now",
        on_click=lambda: open_application(state),
        bg=ACCENT_DARK,
        hover_bg=(42, 74, 130),
        text_color=PANEL,
        border_color=ACCENT_DARK,
        font=make_font(18, bold=True),
    )
    details_apply_bottom = Button(
        pygame.Rect(0, 0, 200, 46),
        "Apply Now",
        on_click=lambda: open_application(state),
        bg=ACCENT_LIGHT,
        hover_bg=ACCENT,
        text_color=ACCENT_DARK,
        border_color=ACCENT_DARK,
        font=make_font(18, bold=True),
    )
    apply_back_button = Button(
        pygame.Rect(0, 0, 88, 40),
        "Back",
        on_click=lambda: go_back_to_details(state),
        bg=PANEL,
        hover_bg=ACCENT_LIGHT,
        border_color=ACCENT_DARK,
        font=make_font(18, bold=True),
    )

    running = True
    result_buttons: List[Button] = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if state.screen == "search" and state.filter_panel_open:
                    state.filter_panel_open = False
                    Dropdown.OPEN_MENU = None
                elif state.screen == "details":
                    go_back_to_search(state)
                elif state.screen == "apply":
                    go_back_to_details(state)
                elif state.screen == "login":
                    running = False

            if state.screen == "login":
                login_button.handle_event(event)

            elif state.screen == "search":
                current_jobs = state.filtered_jobs()
                if state.search_input.handle_event(event):
                    pass
                search_button.handle_event(event)
                filters_button.handle_event(event)
                if state.filter_panel_open:
                    for dropdown in state.dropdowns:
                        dropdown.handle_event(event)
                    reset_button.handle_event(event)
                else:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        Dropdown.OPEN_MENU = None

                for button in result_buttons:
                    button.handle_event(event)

                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and state.search_input.active:
                    pass

                if event.type == pygame.MOUSEWHEEL:
                    if state.filter_panel_open and Dropdown.OPEN_MENU is not None and Dropdown.OPEN_MENU.handle_event(event):
                        pass
                    else:
                        view_height = get_search_list_view_height(state.filter_panel_open)
                        content_height = get_search_content_height(current_jobs, SEARCH_TABLE_WIDTHS, view_height)
                        state.results_scroll.update(-event.y * 48, view_height, content_height)

            elif state.screen == "details":
                details_back_button.handle_event(event)
                details_apply_top.handle_event(event)
                details_apply_bottom.handle_event(event)
                if event.type == pygame.MOUSEWHEEL and state.selected_job is not None:
                    viewport_height = get_main_content_rect().height - 44
                    content_height = get_details_content_height(state.selected_job, get_main_content_rect().width - 48)
                    state.details_scroll.update(-event.y * 48, viewport_height, content_height)

            elif state.screen == "apply":
                apply_back_button.handle_event(event)
                if event.type == pygame.MOUSEWHEEL:
                    state.apply_scroll.update(-event.y * 48, HEIGHT - 286, 980)

        if state.screen == "login":
            draw_login_page(screen, login_button)
        elif state.screen == "search":
            draw_search_page(screen, state, search_button, filters_button, reset_button, result_buttons)
        elif state.screen == "details":
            draw_details_page(screen, state, details_back_button, details_apply_top, details_apply_bottom)
        elif state.screen == "apply":
            draw_apply_page(screen, state, apply_back_button)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
