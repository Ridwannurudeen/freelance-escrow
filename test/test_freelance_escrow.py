from gltest import get_contract_factory, default_account, get_account
from gltest.assertions import tx_execution_succeeded


def deploy_escrow():
    """Deploy the FreelanceEscrow contract with test parameters."""
    factory = get_contract_factory("FreelanceEscrow")
    contract = factory.deploy(
        args=[
            "Build a Landing Page",
            "Create a responsive landing page with hero section, features grid, and contact form",
            72,
        ],
        value=1000000,
    )

    # Verify initial state
    status = contract.get_status(args=[])
    assert status == "open"

    details = contract.get_job_details(args=[])
    assert details["title"] == "Build a Landing Page"
    assert details["status"] == "open"

    return contract


def test_job_creation_and_details():
    """Test that the contract deploys with correct initial state."""
    contract = deploy_escrow()

    details = contract.get_job_details(args=[])
    assert details["title"] == "Build a Landing Page"
    assert details["status"] == "open"
    assert details["payment"] == "1000000"
    assert details["submission_url"] == ""
    assert details["evaluation_result"] == ""


def test_accept_job():
    """Test that a freelancer can accept an open job."""
    contract = deploy_escrow()
    freelancer = get_account(1)

    result = contract.accept_job(args=[], account=freelancer)
    assert tx_execution_succeeded(result)

    status = contract.get_status(args=[])
    assert status == "in_progress"

    details = contract.get_job_details(args=[])
    assert details["freelancer"] == freelancer.address


def test_cancel_job():
    """Test that the client can cancel an open job."""
    contract = deploy_escrow()

    result = contract.cancel_job(args=[])
    assert tx_execution_succeeded(result)

    status = contract.get_status(args=[])
    assert status == "refunded"


def test_cannot_double_accept():
    """Test that a second freelancer cannot accept an already-accepted job."""
    contract = deploy_escrow()
    freelancer1 = get_account(1)
    freelancer2 = get_account(2)

    # First freelancer accepts
    result = contract.accept_job(args=[], account=freelancer1)
    assert tx_execution_succeeded(result)

    # Second freelancer tries to accept - should fail
    try:
        contract.accept_job(args=[], account=freelancer2)
        assert False, "Should have raised an exception"
    except Exception:
        pass

    # Status should still be in_progress with first freelancer
    assert contract.get_status(args=[]) == "in_progress"


def test_client_cannot_accept_own_job():
    """Test that the client cannot accept their own job."""
    contract = deploy_escrow()

    try:
        contract.accept_job(args=[])
        assert False, "Client should not be able to accept own job"
    except Exception:
        pass

    assert contract.get_status(args=[]) == "open"


def test_submit_work():
    """Test the full flow up to work submission."""
    contract = deploy_escrow()
    freelancer = get_account(1)

    contract.accept_job(args=[], account=freelancer)
    assert contract.get_status(args=[]) == "in_progress"

    result = contract.submit_work(
        args=["https://github.com/example/landing-page"],
        account=freelancer,
    )
    assert tx_execution_succeeded(result)
    assert contract.get_status(args=[]) == "submitted"

    details = contract.get_job_details(args=[])
    assert details["submission_url"] == "https://github.com/example/landing-page"


def test_only_freelancer_can_submit():
    """Test that only the assigned freelancer can submit work."""
    contract = deploy_escrow()
    freelancer = get_account(1)
    stranger = get_account(2)

    contract.accept_job(args=[], account=freelancer)

    try:
        contract.submit_work(
            args=["https://example.com/fake"],
            account=stranger,
        )
        assert False, "Stranger should not be able to submit"
    except Exception:
        pass


def test_freelancer_withdraw():
    """Test that a freelancer can withdraw and the job reopens."""
    contract = deploy_escrow()
    freelancer = get_account(1)

    contract.accept_job(args=[], account=freelancer)
    assert contract.get_status(args=[]) == "in_progress"

    result = contract.withdraw_as_freelancer(args=[], account=freelancer)
    assert tx_execution_succeeded(result)
    assert contract.get_status(args=[]) == "open"


def test_cannot_cancel_accepted_job():
    """Test that a client cannot cancel a job after a freelancer accepts."""
    contract = deploy_escrow()
    freelancer = get_account(1)

    contract.accept_job(args=[], account=freelancer)

    try:
        contract.cancel_job(args=[])
        assert False, "Should not cancel an in-progress job"
    except Exception:
        pass

    assert contract.get_status(args=[]) == "in_progress"


def test_full_flow_with_evaluation():
    """Test the complete happy path including AI evaluation."""
    contract = deploy_escrow()
    freelancer = get_account(1)

    # Accept
    contract.accept_job(args=[], account=freelancer)

    # Submit
    contract.submit_work(
        args=["https://github.com/example/landing-page"],
        account=freelancer,
    )
    assert contract.get_status(args=[]) == "submitted"

    # Evaluate (this triggers the AI - may take longer)
    result = contract.evaluate_and_release(
        args=[],
        wait_interval=10000,
        wait_retries=30,
    )
    assert tx_execution_succeeded(result)

    final_status = contract.get_status(args=[])
    assert final_status in ["completed", "refunded"]

    evaluation = contract.get_evaluation(args=[])
    assert len(evaluation) > 0
