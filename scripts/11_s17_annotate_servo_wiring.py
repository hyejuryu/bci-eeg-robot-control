from pathlib import Path
import textwrap

import matplotlib.image as mpimg
import matplotlib.pyplot as plt


def normalized_point(
    width: int,
    height: int,
    x_fraction: float,
    y_fraction: float,
) -> tuple[float, float]:
    """Convert normalized image coordinates to pixel coordinates."""
    return width * x_fraction, height * y_fraction


def add_number_marker(
    ax,
    number: int,
    xy: tuple[float, float],
) -> None:
    """Add a numbered marker directly on the relevant component."""
    x, y = xy

    ax.scatter(
        [x],
        [y],
        s=420,
        facecolors="white",
        edgecolors="black",
        linewidths=1.5,
        zorder=5,
    )

    ax.text(
        x,
        y,
        str(number),
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
        zorder=6,
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]

    input_path = (
        repo_root
        / "media"
        / "session-17"
        / "photos"
        / "validation"
        / "s17_servo_smoke_test_wiring.jpg"
    )

    output_dir = repo_root / "figures" / "session-17"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = (
        output_dir
        / "s17_servo_power_and_signal_wiring_v0.1.png"
    )

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input image not found: {input_path}"
        )

    image = mpimg.imread(input_path)
    height, width = image.shape[:2]

    # Coordinates are normalized to the actual source image.
    # They correspond to the uploaded Session 17 wiring photograph.
    annotations = [
        {
            "number": 1,
            "xy_fraction": (0.44, 0.975),
            "text": (
                "Arduino USB Type-B connection. "
                "The Arduino board was powered from the computer USB port."
            ),
        },
        {
            "number": 2,
            "xy_fraction": (0.37, 0.83),
            "text": (
                "Servo signal path to Arduino D9. "
                "The green jumper shown in the photograph connects "
                "the servo signal path to digital pin 9."
            ),
        },
        {
            "number": 3,
            "xy_fraction": (0.52, 0.72),
            "text": (
                "Arduino GND connection. "
                "This black jumper connects Arduino GND to the "
                "external servo-power GND rail."
            ),
        },
        {
            "number": 4,
            "xy_fraction": (0.84, 0.13),
            "text": (
                "External 5 V adapter connection through the "
                "DC barrel-jack-to-screw-terminal adapter."
            ),
        },
        {
            "number": 5,
            "xy_fraction": (0.505, 0.395),
            "text": (
                "External +5 V rail. "
                "This rail supplies servo V+ through the orange jumper."
            ),
        },
        {
            "number": 6,
            "xy_fraction": (0.53, 0.415),
            "text": (
                "Common GND rail. "
                "External adapter GND, servo GND, and Arduino GND "
                "share this reference."
            ),
        },
        {
            "number": 7,
            "xy_fraction": (0.49, 0.055),
            "text": (
                "1000 µF, 16 V electrolytic capacitor connected "
                "in parallel across the external +5 V and GND rails."
            ),
        },
        {
            "number": 8,
            "xy_fraction": (0.86, 0.56),
            "text": (
                "Tower Pro SG90 servo. "
                "At the servo side: orange is signal, red is V+, "
                "and brown is GND."
            ),
        },
    ]

    fig = plt.figure(figsize=(15, 11))
    grid = fig.add_gridspec(
        nrows=1,
        ncols=2,
        width_ratios=[3.8, 1.5],
        wspace=0.04,
    )

    image_ax = fig.add_subplot(grid[0, 0])
    legend_ax = fig.add_subplot(grid[0, 1])

    image_ax.imshow(image)
    image_ax.axis("off")

    for item in annotations:
        marker_xy = normalized_point(
            width=width,
            height=height,
            x_fraction=item["xy_fraction"][0],
            y_fraction=item["xy_fraction"][1],
        )

        add_number_marker(
            ax=image_ax,
            number=item["number"],
            xy=marker_xy,
        )

    legend_ax.axis("off")
    legend_ax.set_xlim(0, 1)
    legend_ax.set_ylim(0, 1)

    legend_ax.text(
        0.0,
        0.98,
        "Wiring labels",
        ha="left",
        va="top",
        fontsize=13,
        fontweight="bold",
    )

    start_y = 0.92
    spacing = 0.112

    for index, item in enumerate(annotations):
        y = start_y - index * spacing

        legend_ax.text(
            0.0,
            y,
            f"{item['number']}.",
            ha="left",
            va="top",
            fontsize=10,
            fontweight="bold",
        )

        wrapped_text = textwrap.fill(
            item["text"],
            width=38,
        )

        legend_ax.text(
            0.09,
            y,
            wrapped_text,
            ha="left",
            va="top",
            fontsize=9.5,
            linespacing=1.25,
        )

    title = (
        "Session 17 actuator wiring with external 5 V servo power"
    )

    fig.suptitle(
        title,
        fontsize=14,
        y=0.985,
    )

    caption = (
        "The Arduino board was powered through USB, while the SG90 servo "
        "was powered from an external 5 V rail. Arduino GND and the "
        "external servo-power GND rail were connected to provide a "
        "common signal reference."
    )

    fig.text(
        0.04,
        0.02,
        caption,
        ha="left",
        va="bottom",
        fontsize=10,
        wrap=True,
    )

    fig.savefig(
        output_path,
        dpi=200,
        bbox_inches="tight",
    )

    plt.close(fig)

    print(f"Input image size: {width} x {height}")
    print(f"Saved figure: {output_path}")


if __name__ == "__main__":
    main()