from pytest import fixture, mark

from sls.completion.complete import Completion
from sls.document import Document, Position
from sls.services.hub import ServiceHub
from sls.workspace import Workspace

from tests.e2e.utils.fixtures import hub


int_mutations = [
    "absolute",
    "decrement",
    "increment",
    "isEven",
    "isOdd",
]


def document(text):
    doc = Document(".fake.uri.", text)
    return doc


class CompletionTest:
    def __init__(self):
        self.c = Completion.full(ServiceHub(hub))
        self.ws = Workspace(".root_uri.")

    def set(self, text):
        self.doc = document(text)
        return self

    def get_completion_for(self, pos):
        return self.c.complete(ws=self.ws, doc=self.doc, pos=pos)

    def test(self, pos):
        result = self.get_completion_for(Position(*pos))
        # filter only for label for now
        return sorted([k["label"] for k in result["items"]])


@fixture
def completion():
    return CompletionTest()


inline_keywords = ["or", "and", "to"]


@mark.parametrize(
    "text,pos,expected",
    [
        ("ht b", (0, 1), ["http",]),
        ("http b", (0, 5), ["fetch", "server", *inline_keywords]),
    ],
)
def test_complete_service(text, pos, expected, completion):
    assert completion.set(text=text).test(pos) == sorted(expected)


@mark.parametrize(
    "text,pos,expected",
    [
        ("slack send ", (0, 11), ["attachments", "channel", "text", "token"],),
        (
            "http fetch ",
            (0, 11),
            ["body", "headers", "method", "query", "url"],
        ),
        ("oms-services/uuid ", (0, 18), ["generate", *inline_keywords]),
    ],
)
def test_complete_service_arguments(text, pos, expected, completion):
    assert completion.set(text=text).test(pos) == sorted(expected)


def test_complete_dot_additional_blocks(completion):
    text = "arr = [[0]]\n" "foreach arr as e\n" "  arr[0][0].\n" "\n" "a = 1"
    assert sorted(completion.set(text=text).test((2, 12))) == int_mutations


def test_complete_dot_multiple(completion):
    """
    Test that the cache gets properly removed.
    """
    text = "arr = [0]\n" "foreach arr as e8\n" "  e8.\n"
    c = completion.set(text=text)
    res = c.test((2, 4))
    assert res == ["e8"]

    text = "arr = [0]\n" "foreach arr as e9\n" "  e9.\n"
    c = completion.set(text=text)
    res = c.test((2, 4))
    assert res == ["e9"]
