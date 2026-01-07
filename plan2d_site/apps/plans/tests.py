from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from .models import Category, Plan


class PlanReferenceTests(TestCase):
	"""Ensure plan references are generated, stable, and sequential."""

	def setUp(self):
		self.category = Category.objects.create(
			name="Modern",
			description="Modern living",
			display_order=1,
		)

	def _create_plan(self, **overrides):
		payload = {
			'title': overrides.pop('title', 'Sample Plan'),
			'category': self.category,
			'bedrooms': 3,
			'bathrooms': Decimal('2.5'),
			'total_area_sqm': Decimal('120.0'),
			'description': 'Detailed description for testing.',
			'price': Decimal('250.00'),
		}
		payload.update(overrides)
		return Plan.objects.create(**payload)

	def test_reference_is_generated_on_create(self):
		plan = self._create_plan(title='Auto Reference Plan')
		current_year = timezone.now().year
		self.assertTrue(plan.reference.startswith(f"FHP-{current_year}-"))
		self.assertEqual(len(plan.reference.split('-')[-1]), Plan.REFERENCE_SEQUENCE_PADDING)

	def test_reference_is_not_regenerated_on_update(self):
		plan = self._create_plan(title='Immutable Reference Plan')
		existing_reference = plan.reference
		plan.title = 'Updated Title'
		plan.save()
		self.assertEqual(plan.reference, existing_reference)

	def test_sequence_increments_for_same_year(self):
		first_plan = self._create_plan(title='Sequence Alpha')
		second_plan = self._create_plan(title='Sequence Beta')
		first_seq = int(first_plan.reference.split('-')[-1])
		second_seq = int(second_plan.reference.split('-')[-1])
		self.assertEqual(second_seq, first_seq + 1)
