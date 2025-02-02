from mayan.apps.documents.tests.mixins.document_mixins import DocumentTestMixin
from mayan.apps.document_indexing.models import (
    IndexInstanceNode, IndexTemplate
)
from mayan.apps.document_indexing.tests.literals import TEST_INDEX_TEMPLATE_LABEL
from mayan.apps.testing.tests.base import BaseTransactionTestCase

from .literals import (
    TEST_OCR_INDEX_NODE_TEMPLATE, TEST_OCR_INDEX_NODE_TEMPLATE_LEVEL
)


class DocumentVersionOCRIndexingTestCase(DocumentTestMixin, BaseTransactionTestCase):
    auto_upload_test_document = False

    def test_ocr_indexing(self):
        self.test_index_template = IndexTemplate.objects.create(
            label=TEST_INDEX_TEMPLATE_LABEL
        )

        self.test_index_template.document_types.add(self.test_document_type)

        root = self.test_index_template.index_template_root_node
        self.test_index_template.index_template_nodes.create(
            parent=root, expression=TEST_OCR_INDEX_NODE_TEMPLATE,
            link_documents=True
        )

        self._upload_test_document()
        self.test_document.submit_for_ocr()

        self.assertTrue(
            self.test_document in IndexInstanceNode.objects.get(
                value=TEST_OCR_INDEX_NODE_TEMPLATE_LEVEL
            ).documents.all()
        )
