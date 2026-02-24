# SGMAS System Rebuild - Complete Simplification

## Summary
Successfully completed a comprehensive system rebuild to remove unnecessary complexity and implement the correct simplified workflow as per user requirements.

**User's Explicit Requirement:** "remove unnecessary requests PR and MR etc, create pr auto and every fucking unnecessary things"

---

## Correct Simplified Flow

### 1. Production (Production Head)
- Creates Material Request (MR) with items and quantities
- System automatically evaluates inventory availability

### 2. System Auto-Processing
- **Allocates available inventory** to MR (from existing stock)
- **Auto-creates Purchase Request (PR)** for items NOT in stock
- PR status set to: `pending` (no purchaser assigned yet)
- Notifications sent to SCM Planner about new PR

### 3. SCM Planner (Supply Chain Manager)
- Views **Pending PRs** (auto-created, no purchaser assigned)
- Enters **Purchaser Email** for each PR
- Clicks **Assign Button** → PR marked as assigned
- PR status changes to: `assigned`
- Views **Assigned PRs** showing purchaser email and status

### 4. SCM Purchaser (Purchase Specialist)
- Sees **Assigned PRs** (filtered by their email)
- Reviews PR items and details
- **Uploads Purchase Order (PO)** file
- PR status changes to: `po_uploaded`
- PR moves to **"Uploaded Purchase Orders"** section

---

## Files Modified

### 1. Backend: `backend/routes.py`
**Change:** Modified `create_material_request()` endpoint (lines 356-365)
- Auto-creates PurchaseRequest when MR has items to order
- Sets PR status to `pending`
- Populates PR items from `result['to_order']` array
- Creates with no purchaser_email (NULL initially)

**Change:** Modified PATCH `/purchase_requests/<id>/status` endpoint (lines 579-601)
- Now accepts both `status` and `purchaser_email` parameters
- Non-destructive: only updates fields that are provided
- Allows SCM Planner to assign purchaser email
- Allows SCM Purchaser to update status to po_uploaded

### 2. Frontend API: `app/api_client.py`
**Change:** Updated `update_purchase_request_status()` function (lines 91-98)
- Now accepts optional `purchaser_email` parameter
- Builds payload dynamically: only includes provided fields
- Supports both status updates and email assignment

### 3. Frontend UI: `app/scm_chain.py`
**COMPLETE REBUILD of lines 373-450:** SCM Planner section
- **REMOVED:** Material Request display section (was showing MRs from production)
- **REMOVED:** Manual PR creation form (PRs auto-created now)
- **ADDED:** "Pending PRs - Assign to Purchaser" section
  - Shows pending PRs (where purchaser_email is NULL)
  - Text input for purchaser email
  - "Assign" button updates PR with email + status='assigned'
  - Delete button for individual PRs
  - Delete All button for all pending PRs
- **KEPT:** "Assigned PRs" section
  - Shows PRs with purchaser_email set and status != po_uploaded
  - Displays purchaser email, status, created date
  - Shows items list
  - Delete button for each PR
  - Delete All button for all assigned PRs

**SCM Purchaser section:** No changes (already correct - shows assigned PRs filtered by email)

---

## Database Cleanup
Successfully removed all old test data:
- Deleted 12 Material Request Items
- Deleted 8 Material Requests  
- Deleted 0 Purchase Requests
- Database now ready for clean testing

---

## Database Schema (Already in Place)

### PurchaseRequest Model
```python
class PurchaseRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    material_request_id = db.Column(db.Integer, db.ForeignKey("material_requests.id"))
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    purchaser_email = db.Column(db.String(120), nullable=True)  # Assigned by SCM Planner
    status = db.Column(db.String(50), default="draft")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Status Values:**
- `pending` - Auto-created, waiting for purchaser assignment
- `assigned` - Purchaser email set, waiting for PO upload
- `po_uploaded` - PO file uploaded, order complete

---

## Removed Unnecessary Components

1. **Manual PR Creation Form** - PRs now created automatically by system
2. **Material Request Display in Planner View** - SCM Planner only sees PRs, not MRs
3. **Manual PR Status Tracking** - Automated through assignment flow
4. **Redundant Request Types** - Single simplified flow for all material requests

---

## Testing the Flow

### Test Scenario
1. **Production Head:** Creates MR with:
   - 10 units of Item A (in stock)
   - 15 units of Item B (out of stock)
   
2. **Expected Result:**
   - MR created with 10 units allocated to Item A
   - PR auto-created for 15 units of Item B
   - PR status: `pending` with no purchaser_email
   
3. **SCM Planner:**
   - Sees PR in "Pending PRs" section
   - Enters: `purchaser@company.com`
   - Clicks "Assign"
   - PR moves to "Assigned PRs" section
   - PR status: `assigned`
   
4. **SCM Purchaser:**
   - Logs in with email: `purchaser@company.com`
   - Sees PR in "Pending Purchase Requests"
   - Uploads PO file
   - PR moves to "Uploaded Purchase Orders"
   - PR status: `po_uploaded`

---

## System Benefits

✅ **Simplified Flow** - No unnecessary manual steps
✅ **Auto-Inventory** - System automatically handles stock allocation
✅ **Auto-PR Creation** - No manual PR creation needed
✅ **Clear Role Separation:**
  - Production Head: Creates requests
  - SCM Planner: Routes to suppliers
  - SCM Purchaser: Manages orders
  - Inventory Head: Manages stock
✅ **Status Tracking** - Clear progression: pending → assigned → po_uploaded
✅ **Delete Options** - Can remove any PR at any stage
✅ **Clean Database** - Ready for production use

---

## API Endpoints Used

1. `POST /api/material_requests` - Create MR → Auto-creates PR
2. `GET /api/purchase_requests` - List all PRs
3. `PATCH /api/purchase_requests/<id>/status` - Assign purchaser email / Update status
4. `DELETE /api/purchase_requests/<id>` - Delete PR
5. `DELETE /api/purchase_requests/*` - Delete all PRs
6. `GET /api/purchase_requests/assigned` - Get assigned PRs (filtered by email)

---

## Status: READY FOR TESTING

All components have been successfully rebuilt and integrated. Database is clean and ready for fresh testing cycle.
