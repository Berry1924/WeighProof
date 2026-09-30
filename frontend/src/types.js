/**
 * @typedef {Object} Radiologist
 * @property {string} id - Unique Radiologist ID
 * @property {string} name - Full Name
 * @property {string} facility - Facility / Hospital
 * @property {string[]} specialties - Array of specialties e.g. ["CT", "Neuro CT"]
 * @property {boolean} available - Availability state
 * @property {number} current_queue - Current queue length
 * @property {number} capacity_per_hour - Max cases per hour
 * @property {number} active_cases - Active cases count
 * @property {string} status - Status: ACTIVE, UNAVAILABLE, OFF_SHIFT, etc.
 */

/**
 * @typedef {Object} Case
 * @property {string} id - Case ID e.g. RAD-1001
 * @property {string} modality - Modality: CT, MRI, X-Ray, Ultrasound
 * @property {string} exam_type - Exam description e.g. CT Head
 * @property {string} urgency - STAT, URGENT, ROUTINE
 * @property {string} arrival_time - ISO timestamp
 * @property {number} sla_minutes - Target SLA in minutes
 * @property {string} assigned_radiologist_id - Assigned Radiologist ID
 * @property {string} status - Case status: ASSIGNED, REROUTED, ESCALATED
 * @property {string} facility - Facility name
 */

export {};
