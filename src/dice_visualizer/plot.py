import argparse
from functools import lru_cache



def load_plotting_dependencies():
    """Import optional plotting dependencies only when rendering the UI."""
    try:
      import numpy as np
      import matplotlib.pyplot as plt
      from matplotlib.widgets import Button, RadioButtons, Slider
    except ModuleNotFoundError as exc:
      raise RuntimeError(
          "Plotting requires numpy and matplotlib. Install with: python -m pip install -e ."
      ) from exc

    return np, plt, Slider, Button, RadioButtons


def validate_dice_target(n_dice, target_sum):
    """Validate dice count and target sum, returning normalized integers."""
    n_dice = int(n_dice)
    target_sum = int(target_sum)
    if n_dice < 1:
        raise ValueError("Number of dice must be at least 1.")
    min_sum, max_sum = n_dice, 6 * n_dice
    if not (min_sum <= target_sum <= max_sum):
        raise ValueError(
            f"target_sum must be between {min_sum} and {max_sum} for {n_dice} dice."
        )
    return n_dice, target_sum


@lru_cache(maxsize=None)
def count_matching_outcomes(n_dice, target_sum):
    """Count ordered outcomes where n six-sided dice sum to target_sum."""
    n_dice, target_sum = validate_dice_target(n_dice, target_sum)
    if n_dice == 1:
        return 1 if 1 <= target_sum <= 6 else 0
    return sum(
        count_matching_outcomes(n_dice - 1, target_sum - face)
        for face in range(1, 7)
        if n_dice - 1 <= target_sum - face <= 6 * (n_dice - 1)
    )


def plot_ndice(n_dice, target_sum):
    """
    Plot the dice-sum probability space for n_dice, highlighting combinations
    that sum to target_sum.

    For n_dice <= 3: shows the full 1D/2D/3D space.
    For n_dice > 3: shows a 3D slice (three selected dice) and allows moving
    through slices of the remaining dice using a slider / Prev / Next buttons.
    """
    n_dice, target_sum = validate_dice_target(n_dice, target_sum)
    np, plt, Slider, Button, RadioButtons = load_plotting_dependencies()

    # ---- 1D case ----
    if n_dice == 1:
        fig, ax = plt.subplots()
        x = np.arange(1, 7)
        colors = ["red" if xi == target_sum else "lightblue" for xi in x]
        ax.scatter(x, np.zeros_like(x), c=colors, s=250)
        for xi in x:
            ax.text(
                xi,
                0,
                str(xi),
                ha="center",
                va="center",
                color="white" if xi == target_sum else "black",
                fontsize=11,
            )
        ax.set_yticks([])
        ax.set_xlim(0.5, 6.5)
        ax.set_xlabel("Die 1")
        ax.set_title(f"1 die — target sum {target_sum}")
        plt.show()
        return

    # ---- 2D case ----
    if n_dice == 2:
        fig, ax = plt.subplots()
        X, Y = np.meshgrid(np.arange(1, 7), np.arange(1, 7), indexing="ij")
        sums = X + Y
        colors = np.where(sums == target_sum, "red", "lightblue")
        ax.scatter(X.flatten(), Y.flatten(), c=colors.flatten(), s=120)
        ax.set_xlabel("Die 1")
        ax.set_ylabel("Die 2")
        ax.set_xticks(np.arange(1, 7))
        ax.set_yticks(np.arange(1, 7))
        ax.set_title(
            f"2 dice — target sum {target_sum} (matches: {np.sum(sums == target_sum)})"
        )
        ax.set_aspect("equal", adjustable="box")
        plt.show()
        return

    # ---- 3D case ----
    if n_dice == 3:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        A = np.arange(1, 7)
        X, Y, Z = np.meshgrid(A, A, A, indexing="ij")
        sums = X + Y + Z
        mask = sums == target_sum
        ax.scatter(
            X.flatten(),
            Y.flatten(),
            Z.flatten(),
            c=np.where(mask.flatten(), "red", "lightblue"),
            s=30,
        )
        ax.set_xlabel("Die 1")
        ax.set_ylabel("Die 2")
        ax.set_zlabel("Die 3")
        ax.set_title(f"3 dice — target sum {target_sum} (matches: {np.sum(mask)})")
        plt.show()
        return

    # ---- n_dice > 3: interactive slice ----
    extra_dims = n_dice - 3
    total_slices = 6 ** extra_dims  # number of possible slices for remaining dice

    fig = plt.figure(figsize=(11, 6))
    ax_main = fig.add_subplot(121, projection="3d")

    # Radio buttons to pick which dice are X,Y,Z
    labels = [str(i + 1) for i in range(n_dice)]
    ax_rx = fig.add_axes([0.72, 0.78, 0.23, 0.10])
    rx = RadioButtons(ax_rx, labels, active=0)
    ax_rx.set_title("X axis die", fontsize=10)

    ax_ry = fig.add_axes([0.72, 0.64, 0.23, 0.10])
    ry = RadioButtons(ax_ry, labels, active=1)
    ax_ry.set_title("Y axis die", fontsize=10)

    ax_rz = fig.add_axes([0.72, 0.50, 0.23, 0.10])
    rz = RadioButtons(ax_rz, labels, active=2)
    ax_rz.set_title("Z axis die", fontsize=10)

    # Slider for choosing the slice of the remaining dice
    ax_slider = fig.add_axes([0.20, 0.08, 0.45, 0.03])
    slice_slider = Slider(
        ax_slider,
        "Slice",
        0,
        total_slices - 1,
        valinit=0,
        valstep=1,
    )

    # Prev / Next buttons
    ax_prev = fig.add_axes([0.20, 0.02, 0.08, 0.04])
    ax_next = fig.add_axes([0.30, 0.02, 0.08, 0.04])
    btn_prev = Button(ax_prev, "Prev")
    btn_next = Button(ax_next, "Next")

    state = {"x": 0, "y": 1, "z": 2}

    A = np.arange(1, 7)
    X, Y, Z = np.meshgrid(A, A, A, indexing="ij")

    info_text = fig.text(0.72, 0.40, "", fontsize=9)

    def slice_values(idx, indices):
        values = []
        for _ in indices:
            values.append((idx % 6) + 1)
            idx //= 6
        return values

    def render(slice_idx):
        x_idx, y_idx, z_idx = state["x"], state["y"], state["z"]
        selected = {x_idx, y_idx, z_idx}
        remaining = [i for i in range(n_dice) if i not in selected]

        fixed_vals = slice_values(int(slice_idx), remaining)
        fixed_sum = sum(fixed_vals)

        total = X + Y + Z + fixed_sum
        mask = total == target_sum

        ax_main.cla()
        ax_main.scatter(
            X.flatten(),
            Y.flatten(),
            Z.flatten(),
            c=np.where(mask.flatten(), "red", "lightblue"),
            s=22,
        )
        ax_main.set_xlabel(f"Die {x_idx + 1}")
        ax_main.set_ylabel(f"Die {y_idx + 1}")
        ax_main.set_zlabel(f"Die {z_idx + 1}")
        ax_main.set_title(
            f"{n_dice} dice — target sum {target_sum} "
            f"(matches: {int(np.sum(mask))})"
        )

        if remaining:
            parts = [f"Die {i + 1} = {v}" for i, v in zip(remaining, fixed_vals)]
            info_text.set_text("Fixed dice: " + ", ".join(parts))
        else:
            info_text.set_text("")

        fig.canvas.draw_idle()

    def on_radio_x(label):
        state["x"] = int(label) - 1
        render(slice_slider.val)

    def on_radio_y(label):
        state["y"] = int(label) - 1
        render(slice_slider.val)

    def on_radio_z(label):
        state["z"] = int(label) - 1
        render(slice_slider.val)

    def on_slider_change(val):
        render(val)

    def on_prev(event):
        new_val = max(slice_slider.val - 1, 0)
        slice_slider.set_val(new_val)

    def on_next(event):
        new_val = min(slice_slider.val + 1, total_slices - 1)
        slice_slider.set_val(new_val)

    rx.on_clicked(on_radio_x)
    ry.on_clicked(on_radio_y)
    rz.on_clicked(on_radio_z)
    slice_slider.on_changed(on_slider_change)
    btn_prev.on_clicked(on_prev)
    btn_next.on_clicked(on_next)

    render(0)
    plt.show()




def main(argv=None):
    parser = argparse.ArgumentParser(description="Visualize dice-sum probability spaces.")
    parser.add_argument("--dice", type=int, default=4, help="Number of six-sided dice")
    parser.add_argument("--target", type=int, default=14, help="Target sum to highlight")
    args = parser.parse_args(argv)
    plot_ndice(args.dice, args.target)


if __name__ == "__main__":
    main()
