"""
Reusable threshold and dwell decision logic.

This module does not load datasets, calibrate thresholds,
apply smoothing, or write session output files.
"""

from dataclasses import dataclass
import math


LOW_EVIDENCE_STATE = "LOW_ALPHA"
HIGH_EVIDENCE_STATE = "HIGH_ALPHA"
UNAVAILABLE_EVIDENCE_STATE = "UNAVAILABLE"

OPEN_COMMAND_STATE = "CMD_OPEN"
CLOSE_COMMAND_STATE = "CMD_CLOSE"
STOP_COMMAND_STATE = "CMD_STOP"


@dataclass
class DwellDecisionState:
    """
    Internal state retained between decision updates.

    active_evidence_state:
        Evidence state that has already satisfied
        the dwell requirement.

    pending_evidence_state:
        Candidate evidence state that has not yet
        satisfied the dwell requirement.

    pending_count:
        Number of consecutive updates supporting
        the pending evidence state.
    """

    active_evidence_state: str | None = None
    pending_evidence_state: str | None = None
    pending_count: int = 0


@dataclass(frozen=True)
class DwellUpdateResult:
    """
    Observable result produced for one update.
    """

    evidence_state: str
    candidate_evidence_state: str | None
    candidate_count: int
    active_evidence_state: str | None
    initial_command_confirmed: bool
    active_switch_confirmed: bool
    command_state: str


def classify_threshold_state(
    processed_feature_value,
    threshold_value,
):
    """
    Compare one processed feature with a threshold.

    Mapping:
        processed_feature_value >= threshold_value
            -> HIGH_ALPHA

        processed_feature_value < threshold_value
            -> LOW_ALPHA
    """

    processed_value = float(
        processed_feature_value
    )

    threshold = float(
        threshold_value
    )

    if (
        not math.isfinite(processed_value)
        or processed_value <= 0.0
    ):
        raise ValueError(
            "The processed feature value must "
            "be finite and positive."
        )

    if (
        not math.isfinite(threshold)
        or threshold <= 0.0
    ):
        raise ValueError(
            "The threshold value must be "
            "finite and positive."
        )

    if processed_value >= threshold:
        return HIGH_EVIDENCE_STATE

    return LOW_EVIDENCE_STATE


def command_from_evidence_state(
    evidence_state,
):
    """
    Map an evidence state to its command state.
    """

    if evidence_state == LOW_EVIDENCE_STATE:
        return OPEN_COMMAND_STATE

    if evidence_state == HIGH_EVIDENCE_STATE:
        return CLOSE_COMMAND_STATE

    if (
        evidence_state
        == UNAVAILABLE_EVIDENCE_STATE
    ):
        return STOP_COMMAND_STATE

    raise ValueError(
        "Unexpected evidence state: "
        f"{evidence_state}"
    )


def update_dwell_decision(
    state,
    evidence_state,
    dwell_updates,
):
    """
    Apply one evidence update to a dwell state machine.

    The same dwell requirement is used for:
        1. initial active-command confirmation
        2. later active-command switching

    Input:
        state:
            Mutable DwellDecisionState retained
            between updates.

        evidence_state:
            LOW_ALPHA, HIGH_ALPHA, or UNAVAILABLE.

        dwell_updates:
            Required number of consecutive
            available updates with the same state.

    Output:
        DwellUpdateResult describing the current
        candidate, active state, confirmation flags,
        and command output.
    """

    if not isinstance(
        state,
        DwellDecisionState,
    ):
        raise TypeError(
            "state must be a "
            "DwellDecisionState instance."
        )

    if (
        not isinstance(dwell_updates, int)
        or dwell_updates < 1
    ):
        raise ValueError(
            "dwell_updates must be a positive "
            "integer."
        )

    initial_command_confirmed = False
    active_switch_confirmed = False

    candidate_state_for_update = None
    candidate_count_for_update = 0

    if (
        evidence_state
        == UNAVAILABLE_EVIDENCE_STATE
    ):
        if (
            state.active_evidence_state is not None
            or state.pending_evidence_state is not None
            or state.pending_count != 0
        ):
            raise RuntimeError(
                "UNAVAILABLE evidence is supported "
                "only before dwell processing begins."
            )

        return DwellUpdateResult(
            evidence_state=evidence_state,
            candidate_evidence_state=None,
            candidate_count=0,
            active_evidence_state=None,
            initial_command_confirmed=False,
            active_switch_confirmed=False,
            command_state=STOP_COMMAND_STATE,
        )

    if evidence_state not in {
        LOW_EVIDENCE_STATE,
        HIGH_EVIDENCE_STATE,
    }:
        raise ValueError(
            "Unexpected available evidence state: "
            f"{evidence_state}"
        )

    if state.active_evidence_state is None:
        if (
            state.pending_evidence_state
            == evidence_state
        ):
            state.pending_count += 1
        else:
            state.pending_evidence_state = (
                evidence_state
            )

            state.pending_count = 1

        candidate_state_for_update = (
            state.pending_evidence_state
        )

        candidate_count_for_update = (
            state.pending_count
        )

        if (
            state.pending_count
            >= dwell_updates
        ):
            state.active_evidence_state = (
                evidence_state
            )

            initial_command_confirmed = True

            state.pending_evidence_state = None
            state.pending_count = 0

    elif (
        evidence_state
        == state.active_evidence_state
    ):
        state.pending_evidence_state = None
        state.pending_count = 0

    else:
        if (
            state.pending_evidence_state
            == evidence_state
        ):
            state.pending_count += 1
        else:
            state.pending_evidence_state = (
                evidence_state
            )

            state.pending_count = 1

        candidate_state_for_update = (
            state.pending_evidence_state
        )

        candidate_count_for_update = (
            state.pending_count
        )

        if (
            state.pending_count
            >= dwell_updates
        ):
            state.active_evidence_state = (
                evidence_state
            )

            active_switch_confirmed = True

            state.pending_evidence_state = None
            state.pending_count = 0

    if state.active_evidence_state is None:
        command_state = STOP_COMMAND_STATE
    else:
        command_state = (
            command_from_evidence_state(
                state.active_evidence_state
            )
        )

    return DwellUpdateResult(
        evidence_state=evidence_state,
        candidate_evidence_state=(
            candidate_state_for_update
        ),
        candidate_count=(
            candidate_count_for_update
        ),
        active_evidence_state=(
            state.active_evidence_state
        ),
        initial_command_confirmed=(
            initial_command_confirmed
        ),
        active_switch_confirmed=(
            active_switch_confirmed
        ),
        command_state=command_state,
    )