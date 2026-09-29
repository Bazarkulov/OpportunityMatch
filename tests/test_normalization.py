from backend.normalization import RawOpportunity, normalize
def test_normalization_extracts_only_explicit_information():
    raw=RawOpportunity("42","Robotics Research Internship","Public Lab","test","https://example.edu/42","Berlin, Germany","<p>Open to undergraduate students. Requirements: experience with Python and Computer Vision. Minimum GPA: 3.2/4.0. Paid stipend.</p>"); result=normalize(raw)
    assert result["degree_requirements"]==["Bachelor's"]; assert result["minimum_gpa"]==3.2; assert result["funding_status"]=="Paid"; assert "Python" in result["required_skills"]; assert result["nationality_restrictions"] is None; assert result["language_requirements"] is None
def test_absent_requirements_remain_unknown():
    result=normalize(RawOpportunity("1","Student Fellowship","Public Lab","test","https://example.edu/1",None,"Learn with our team")); assert result["minimum_gpa"] is None; assert result["degree_requirements"] is None; assert result["remote"] is None
