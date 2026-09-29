from backend.collectors.greenhouse import GreenhouseCollector
from backend.collectors.lever import LeverCollector
def test_greenhouse_parser_filters_non_student_jobs():
    collector=GreenhouseCollector("test"); collector.get_json=lambda url: {"name":"University Lab"} if "jobs?" not in url else {"jobs":[{"id":1,"title":"Research Intern","updated_at":"2026-01-01T00:00:00Z","absolute_url":"https://example.edu/1","location":{"name":"Boston"},"content":"Undergraduate research"},{"id":2,"title":"Senior Director","absolute_url":"https://example.edu/2","location":{"name":"Boston"},"content":"Executive leadership"}]}
    records=collector.collect(); assert len(records)==1; assert records[0].external_id=="1"
def test_lever_parser_maps_public_posting():
    collector=LeverCollector("public-lab"); collector.get_json=lambda _: [{"id":"abc","text":"Software Intern","hostedUrl":"https://jobs.lever.co/public-lab/abc","categories":{"location":"Remote"},"descriptionPlain":"Student internship","description":"<p>Python</p>","lists":[]}]
    records=collector.collect(); assert len(records)==1; assert records[0].location=="Remote"
