# Example Prompts for Auto Surveyor Task Creation

This document provides example prompts you can use with the AI task creation feature for auto surveying tasks, along with the expected AI-generated output.

## Example 1: Basic Vehicle Survey

**Prompt:**
```
Survey completed for VIN WB02A1234 near Indore. Minor rear damage. Assign to Ramesh. Due tomorrow.
```

**AI-Generated Output:**
```json
{
  "title": "Survey for VIN WB02A1234",
  "description": "Vehicle details:\n- VIN: WB02A1234\n- Location: Indore\n\nDamage description:\n- Minor rear damage\n\nSpecial instructions:\n- None specified",
  "priority": "Medium",
  "category_id": 1,
  "due_date": "2025-05-05",
  "assigned_to": "Ramesh"
}
```

## Example 2: Urgent Damage Assessment

**Prompt:**
```
Urgent: Need damage assessment for Honda Civic with VIN 1HGCM82633A123456 involved in major collision in Mumbai. Customer needs report for insurance claim by end of day. Severe front-end damage with airbag deployment.
```

**AI-Generated Output:**
```json
{
  "title": "Urgent Damage Assessment - Honda Civic (1HGCM82633A)",
  "description": "Vehicle details:\n- Make/Model: Honda Civic\n- VIN: 1HGCM82633A123456\n- Location: Mumbai\n\nDamage description:\n- Severe front-end damage\n- Airbag deployment\n- Major collision\n\nSpecial instructions:\n- Customer needs report for insurance claim\n- High priority due to severity",
  "priority": "High",
  "category_id": 2,
  "due_date": "2025-05-04"
}
```

## Example 3: Claims Processing Task

**Prompt:**
```
Process insurance claim for Toyota Fortuner (VIN MHFYZ59G7KP085421) surveyed last week. All documentation received from customer. Moderate damage to driver side door and fender. Insurance company: ICICI Lombard. Policy #: IL-AUTO-12345.
```

**AI-Generated Output:**
```json
{
  "title": "Process Insurance Claim - Toyota Fortuner",
  "description": "Vehicle details:\n- Make/Model: Toyota Fortuner\n- VIN: MHFYZ59G7KP085421\n\nDamage description:\n- Moderate damage to driver side door and fender\n\nInsurance details:\n- Company: ICICI Lombard\n- Policy #: IL-AUTO-12345\n\nSpecial instructions:\n- All documentation received from customer\n- Vehicle was surveyed last week",
  "priority": "Medium",
  "category_id": 3,
  "due_date": "2025-05-11"
}
```

## Example 4: Final Inspection Task

**Prompt:**
```
Final inspection needed for Maruti Swift (VIN MA3EWDE1S00152437) at Sharma Motors workshop in Delhi. Repairs completed after rear-end collision. Verify paint matching and bumper alignment. Assign to Vikram for Thursday.
```

**AI-Generated Output:**
```json
{
  "title": "Final Inspection - Maruti Swift",
  "description": "Vehicle details:\n- Make/Model: Maruti Swift\n- VIN: MA3EWDE1S00152437\n- Location: Sharma Motors workshop, Delhi\n\nInspection focus:\n- Paint matching verification\n- Bumper alignment check\n- Overall repair quality after rear-end collision\n\nSpecial instructions:\n- Repairs have been completed\n- Final verification before customer delivery",
  "priority": "Medium",
  "category_id": 4,
  "due_date": "2025-05-08",
  "assigned_to": "Vikram"
}
```

## Example 5: Initial Survey with Specific Details

**Prompt:**
```
New survey request for Hyundai i20 with suspected engine damage. Vehicle located at customer's residence in Pune (Aundh area). VIN MALBA51BLCM123456. Contact Mr. Patel at 9876543210. High priority as customer is demanding quick resolution.
```

**AI-Generated Output:**
```json
{
  "title": "Initial Survey - Hyundai i20 Engine Damage",
  "description": "Vehicle details:\n- Make/Model: Hyundai i20\n- VIN: MALBA51BLCM123456\n- Location: Customer's residence in Pune (Aundh area)\n\nDamage description:\n- Suspected engine damage\n\nContact information:\n- Mr. Patel: 9876543210\n\nSpecial instructions:\n- Customer is demanding quick resolution\n- High priority case",
  "priority": "High",
  "category_id": 1,
  "due_date": "2025-05-05"
}
```

## Example 6: Voice Input for Survey Task

When using voice input, you might say:

**Voice Input:**
```
"Need to conduct damage assessment for a Mahindra XUV700 with VIN number MALBB51BLCM987654 at Royal Motors garage in Chennai. The vehicle has moderate damage to the front bumper and headlights from a parking accident. Please assign this to Suresh and make sure it's completed by Friday."
```

**AI-Generated Output:**
```json
{
  "title": "Damage Assessment - Mahindra XUV700",
  "description": "Vehicle details:\n- Make/Model: Mahindra XUV700\n- VIN: MALBB51BLCM987654\n- Location: Royal Motors garage, Chennai\n\nDamage description:\n- Moderate damage to front bumper\n- Damaged headlights\n- Caused by parking accident\n\nSpecial instructions:\n- Standard assessment procedure\n- Document with photographs",
  "priority": "Medium",
  "category_id": 2,
  "due_date": "2025-05-09",
  "assigned_to": "Suresh"
}
```

## Tips for Effective Auto Surveyor Prompts

1. **Include vehicle identification** (make, model, VIN) when available
2. **Specify the location** of the vehicle
3. **Describe the damage** clearly and its severity
4. **Mention deadlines** when applicable
5. **Indicate priority level** for urgent cases
6. **Specify who should be assigned** to the task if known
7. **Include relevant insurance details** for claims processing tasks
8. **Mention special circumstances** that might affect the survey

The AI will extract the most relevant information and structure it appropriately, but you can always adjust the generated details before creating the task.
