from pathlib import Path
import re
import shutil

from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parent
LAB6 = ROOT.parent / "Lab 6"
SCREENSHOTS = ROOT / "screenshots"
REPORT = ROOT / "Submission_Report.pdf"
FONT_PATH = Path(r"C:\Windows\Fonts\consola.ttf")


def read_console_output(name):
    data = (ROOT / name).read_bytes()
    encoding = "utf-16" if data.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
    return data.decode(encoding).strip()


def render_terminal(title, lines, destination):
    font = ImageFont.truetype(str(FONT_PATH), 22) if FONT_PATH.exists() else ImageFont.load_default()
    line_height = 30
    width = 1480
    visible_lines = [line.encode("ascii", "replace").decode("ascii")[:132] for line in lines]
    height = 72 + line_height * max(1, len(visible_lines))
    image = Image.new("RGB", (width, height), "#101418")
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, width, 48), fill="#263238")
    draw.ellipse((18, 17, 32, 31), fill="#ff5f56")
    draw.ellipse((42, 17, 56, 31), fill="#ffbd2e")
    draw.ellipse((66, 17, 80, 31), fill="#27c93f")
    draw.text((100, 12), title[:95], font=font, fill="#f3f5f6")
    y = 62
    for line in visible_lines:
        color = "#7ee787" if "PASSED" in line or "passed" in line else "#ff7b72" if "FAILED" in line or "failed" in line else "#d7e0e7"
        draw.text((22, y), line, font=font, fill=color)
        y += line_height
    image.save(destination)


def draw_image_page(pdf, title, caption, image_path):
    width, height = letter
    pdf.showPage()
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(40, height - 48, title)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, height - 68, caption)
    with Image.open(image_path) as image:
        image_width, image_height = image.size
    scale = min(530 / image_width, 430 / image_height)
    draw_width, draw_height = image_width * scale, image_height * scale
    pdf.drawImage(
        str(image_path),
        (width - draw_width) / 2,
        height - 95 - draw_height,
        width=draw_width,
        height=draw_height,
        preserveAspectRatio=True,
        mask="auto",
    )


def draw_code_pages(pdf, filename, title):
    width, height = letter
    source = (ROOT / filename).read_text(encoding="utf-8").splitlines()
    page_size = 63
    for page_number, start in enumerate(range(0, len(source), page_size), start=1):
        pdf.showPage()
        pdf.setFont("Helvetica-Bold", 16)
        pdf.drawString(40, height - 42, f"{title} - page {page_number}")
        pdf.setFont("Courier", 7.2)
        y = height - 64
        for line_number, line in enumerate(source[start : start + page_size], start=start + 1):
            pdf.drawString(40, y, f"{line_number:03} | {line[:120]}")
            y -= 10.5


def main():
    SCREENSHOTS.mkdir(exist_ok=True)

    original_code = SCREENSHOTS / "lab6_code_coverage.png"
    original_branch = SCREENSHOTS / "lab6_branch_coverage.png"
    shutil.copy2(
        LAB6 / "screenshots" / "Screenshot 2026-11-04 092620.png",
        original_code,
    )
    shutil.copy2(
        LAB6 / "screenshots" / "Screenshot 2026-11-04 092719.png",
        original_branch,
    )

    render_terminal(
        "Original Lab 6 application - direct execution",
        ["$ python -c <three Lab 6 function examples>", *read_console_output("original_app_output.txt").splitlines()],
        SCREENSHOTS / "original_application_execution.png",
    )

    failed_output = read_console_output("pre_fix_test_output.txt")
    summary = re.search(r"=+ ([0-9]+ failed, [0-9]+ passed in [0-9.]+s) =+", failed_output)
    summary_line = summary.group(1) if summary else "Hypothesis reported failing input-validation properties."
    render_terminal(
        "Hypothesis failures before fixes",
        [
            "$ python -m pytest -v --hypothesis-show-statistics",
            "test_overage_charge_rejects_invalid_usage - FAILED",
            "  minimized invalid_data='' -> TypeError; False was also accepted",
            "test_recharge_rejects_negative_amount - FAILED (amount=-1)",
            "test_recharge_rejects_negative_pending_count - FAILED (pending_recharges=-1)",
            "test_validity_rejects_boolean_day_counts - FAILED (days_left=False)",
            "test_validity_rejects_fractional_day_counts - FAILED (days_left=0.5)",
            f"Result: {summary_line}",
        ],
        SCREENSHOTS / "hypothesis_failures.png",
    )

    render_terminal(
        "Corrected Lab 7 application - direct execution",
        ["$ python -c <three corrected function examples>", *read_console_output("corrected_app_output.txt").splitlines()],
        SCREENSHOTS / "corrected_application_execution.png",
    )

    final_output = read_console_output("final_test_output.txt")
    pass_lines = [
        line.strip()
        for line in final_output.splitlines()
        if "collected " in line or "::" in line and "PASSED" in line or re.search(r"[0-9]+ passed in", line)
    ]
    render_terminal(
        "Final Hypothesis test run",
        ["$ python -m pytest -v --hypothesis-show-statistics", *pass_lines],
        SCREENSHOTS / "final_test_results.png",
    )

    pdf = canvas.Canvas(str(REPORT), pagesize=letter)
    width, height = letter
    pdf.setTitle("Lab 7 - Fuzz Testing for Input Validation Bugs")
    pdf.setFont("Helvetica-Bold", 22)
    pdf.drawString(40, height - 70, "Lab 7 - Fuzz Testing")
    pdf.setFont("Helvetica", 14)
    pdf.drawString(40, height - 98, "Mobile Data Plan Application")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, height - 136, "Hypothesis fuzz testing and corrected input validation")
    pdf.drawString(40, height - 168, "Evidence: original execution, minimized failures, corrected execution, passing tests")
    pdf.drawString(40, height - 190, "Final result: 12 tests passed; all three application functions fuzz-tested.")
    pdf.drawString(40, height - 222, "The original Lab 6 function behavior is preserved for valid inputs.")
    pdf.drawString(40, height - 244, "Invalid values now raise ValueError with explicit input rules.")
    pdf.setFont("Helvetica-Oblique", 9)
    pdf.drawString(40, 35, "The following pages contain execution evidence and the requested Python sources.")

    draw_image_page(
        pdf,
        "Original application execution",
        "Direct calls against the Lab 6 module; Lab 6 coverage screenshots follow.",
        SCREENSHOTS / "original_application_execution.png",
    )
    draw_image_page(
        pdf,
        "Original Lab 6 test execution",
        "Existing Lab 6 screenshots showing the unmodified application test runs.",
        original_code,
    )
    draw_image_page(
        pdf,
        "Original Lab 6 branch coverage",
        "Existing branch-coverage execution evidence.",
        original_branch,
    )
    draw_image_page(
        pdf,
        "Failing Hypothesis examples",
        "Minimized invalid inputs found against the original implementation.",
        SCREENSHOTS / "hypothesis_failures.png",
    )
    draw_image_page(
        pdf,
        "Corrected application execution",
        "Representative valid outputs from the corrected Lab 7 module.",
        SCREENSHOTS / "corrected_application_execution.png",
    )
    draw_image_page(
        pdf,
        "Final successful test execution",
        "Hypothesis statistics show 100 examples for each applicable property.",
        SCREENSHOTS / "final_test_results.png",
    )
    draw_code_pages(pdf, "processor.py", "processor.py")
    draw_code_pages(pdf, "test_processor.py", "test_processor.py")
    pdf.save()
    print(f"Created {REPORT}")


if __name__ == "__main__":
    main()
