# Business scenarios: {{feature}}

Version: {{version}} · Date: {{date}} · Author: {{author}} · Sources: {{sources}}

## 1. Overview
- Goal:
- Actors and roles:
- Screens: <!-- screen IDs and routes -->
- In scope / out of scope:

## 2. Business rules
| ID | Rule | Source | Enforced in | Status |
| -- | ---- | ------ | ----------- | ------ |
| BR-<AREA>-001 | | <!-- doc §, ticket, client decision --> | FE / BE / both | confirmed / needs confirmation |

## 3. Data rules
| Field | Label (product language) | Type | Required | Limits / format | Default | Source of value |
| ----- | ------------------------ | ---- | -------- | --------------- | ------- | --------------- |

## 4. Scenarios

### SCN-<AREA>-01 <name>
- Goal:
- Actor:
- Preconditions:
- Trigger:

**Main flow**
1. <actor> <action> → <system shows> (`<exact UI label>`)
2.

**Alternative flows**
- A1 (at step N, when <condition>): <steps>, then back to step M.

**Exception flows**
- E1 (when <condition>): system shows `<exact message>` (`<error.code>`); user can <recovery>.

**Postconditions:**
**Business rules:** BR-<AREA>-001
**Test cases:** TC-<AREA>-001…

## 5. States and transitions
| State | What the user sees | What the user can do |
| ----- | ------------------ | -------------------- |

<!-- Each allowed transition once; forbidden ones the UI or API could still be asked for, with the expected refusal. -->
| From | Action | To | Allowed | Source | Test case |
| ---- | ------ | -- | ------- | ------ | --------- |

## 6. Decision tables
<!-- Only where several conditions combine to decide the result. One column per combination that changes the result. -->
| Condition / result | 1 | 2 | 3 |
| ------------------ | - | - | - |
| <condition> | Y | N | Y |
| **Result** | | | |

## 7. Test data
| Need | Value or how it is made | Used by |
| ---- | ----------------------- | ------- |
| <role / status> account | <!-- where it is defined (seed file); never a password --> | |
| Records in state <state> | <!-- seed, fixture, local mock --> | |
| List sizes | 0 · 1 · one page · one page + 1 | |

## 8. Open questions
| ID | Question | Owner | Blocking | Status | Answer |
| -- | -------- | ----- | -------- | ------ | ------ |

## 9. Coverage
| Item (BR / flow / transition / decision column) | Test cases | Gap |
| ----------------------------------------------- | ---------- | --- |
