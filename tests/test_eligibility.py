from backend.eligibility import evaluate_eligibility
def student(**overrides):
    value={"degree_level":"Bachelor's","major":"Robotics","nationality":"Kazakhstani","gpa":3.6,"gpa_scale":4.0,"languages":{"English":"Professional Fluency"}}; value.update(overrides); return value
def opportunity(**overrides):
    value={"degree_requirements":["Bachelor's"],"major_requirements":["Robotics"],"nationality_restrictions":["any"],"minimum_gpa":3.0,"gpa_scale":4.0,"language_requirements":{"English":"Conversational"}}; value.update(overrides); return value
def test_all_explicit_rules_pass():
    result=evaluate_eligibility(student(),opportunity()); assert result["status"]=="eligible"; assert not result["failed"]; assert not result["unknown"]
def test_explicit_failure_is_ineligible():
    result=evaluate_eligibility(student(gpa=2.5),opportunity()); assert result["status"]=="ineligible"; assert any("below" in x for x in result["failed"])
def test_omitted_requirements_are_uncertain_not_failed():
    result=evaluate_eligibility(student(),opportunity(degree_requirements=None,major_requirements=None,nationality_restrictions=None,minimum_gpa=None,language_requirements=None)); assert result["status"]=="uncertain"; assert not result["failed"]; assert len(result["unknown"])==5
def test_missing_required_language_fails():
    result=evaluate_eligibility(student(languages={}),opportunity()); assert result["status"]=="ineligible"; assert any("English" in x for x in result["failed"])
