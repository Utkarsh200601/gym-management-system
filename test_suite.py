"""Automated Verification Suite for Gym & Fitness Management System.

Tests all CRUD operations, search filters, and integrity constraints.
"""

from db_helper import Database


def run_tests():
    print("==================================================================")
    print("RUNNING AUTOMATED VERIFICATION TEST SUITE")
    print("==================================================================")

    db = Database()
    # Test connection to MySQL or switch to local storage
    is_online, conn_msg = db.test_connection()
    if is_online:
        print(f"[PASS] MySQL Server Online: {conn_msg}")
    else:
        print(f"[INFO] MySQL Server is currently offline: {conn_msg}")
        print("[INFO] Engaging Local Storage Verification Engine...")
        db.enable_demo_mode()

    # 1. Test Fetch All
    success, members, msg = db.fetch_all_members()
    assert success, f"Failed to fetch members: {msg}"
    assert len(members) >= 5, f"Expected at least 5 initial members, got {len(members)}"
    print(f"[PASS] fetch_all_members(): Retrieved {len(members)} records successfully.")

    # 2. Test Search
    success, results, msg = db.search_members("Connor", "Name")
    assert success, f"Search failed: {msg}"
    assert len(results) >= 1, "Expected to find Sarah Connor"
    print(f"[PASS] search_members('Connor', 'Name'): Found {len(results)} matching record(s).")

    # 3. Test Add Member
    success, add_msg, new_id = db.add_member(
        name="Test Athlete",
        phone="555-9988",
        email="test.athlete@example.com",
        join_date="2026-10-26",
        plan_type="Annual",
        status="Active",
    )
    assert success, f"Failed to add member: {add_msg}"
    assert new_id is not None, "New member_id should not be None"
    print(f"[PASS] add_member(): {add_msg}")

    # 4. Test Duplicate Prevention
    dup_success, dup_msg, _ = db.add_member(
        name="Duplicate Athlete",
        phone="555-9988",  # duplicate phone
        email="another@example.com",
        join_date="2026-10-26",
        plan_type="Monthly",
        status="Active",
    )
    assert not dup_success, "Duplicate phone insertion should have been rejected!"
    print(f"[PASS] Duplicate Prevention: Correctly rejected duplicate entry ({dup_msg})")

    # 5. Test Update Member
    update_success, update_msg = db.update_member(
        member_id=new_id,
        name="Test Athlete Updated",
        phone="555-9988",
        email="test.athlete.updated@example.com",
        join_date="2026-10-26",
        plan_type="Quarterly",
        status="Active",
    )
    assert update_success, f"Failed to update member: {update_msg}"
    print(f"[PASS] update_member(): {update_msg}")

    # 6. Test Delete Member
    del_success, del_msg = db.delete_member(new_id)
    assert del_success, f"Failed to delete member: {del_msg}"
    print(f"[PASS] delete_member(): {del_msg}")

    # 7. Verify deletion
    _, after_del, _ = db.fetch_all_members()
    assert all(m["member_id"] != new_id for m in after_del), "Deleted member still present in records!"
    print("[PASS] Verification of Deletion: Member confirmed removed.")

    print("==================================================================")
    print("ALL TESTS PASSED WITH 100% SUCCESS!")
    print("==================================================================")


if __name__ == "__main__":
    run_tests()
