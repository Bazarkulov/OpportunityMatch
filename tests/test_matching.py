import pytest
from backend.matching import score_relevance
STUDENT={"major":"Robotics","skills":["Python","ROS2","Computer Vision"],"interests":["robotics","autonomous systems"],"preferred_opportunity_types":["Research Internship"],"preferred_locations":["Germany"],"remote_preference":False}
ROBOTICS={"required_skills":["Python","ROS2"],"preferred_skills":["Computer Vision","C++"],"fields":["Robotics","Engineering"],"keywords":["autonomous systems"],"opportunity_type":"Research Internship","location":"Munich, Germany","remote":False}
FINANCE={"required_skills":["Accounting","Excel"],"preferred_skills":["Financial reporting"],"fields":["Finance","Accounting"],"keywords":["audit"],"opportunity_type":"Internship","location":"New York, USA","remote":False}
def test_obvious_relevant_opportunity_ranks_substantially_higher():
    relevant=score_relevance(STUDENT,ROBOTICS); unrelated=score_relevance(STUDENT,FINANCE); assert relevant["overall_score"] >= unrelated["overall_score"]+40; assert "Python" in relevant["matched_characteristics"]; assert "C++" in relevant["missing_preferred_characteristics"]
def test_weights_must_sum_to_one():
    with pytest.raises(ValueError): score_relevance(STUDENT,ROBOTICS,weights={"skill_overlap":.5})
