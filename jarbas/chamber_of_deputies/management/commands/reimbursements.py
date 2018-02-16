import lzma
from csv import DictReader

from jarbas.core.management.commands import LoadCommand
from jarbas.chamber_of_deputies.models import Reimbursement
from jarbas.chamber_of_deputies.tasks import create_or_update_reimbursement


class Command(LoadCommand):
    help = 'Load Serenata de Amor reimbursements dataset'

    def handle(self, *args, **options):
        self.path = options['dataset']

        if options.get('drop', False):
            self.drop_all(Reimbursement)

        self.create_or_update(self.reimbursements)

    @property
    def reimbursements(self):
        """Returns a Generator with a dict object for each row."""
        with lzma.open(self.path, 'rt') as file_handler:
            yield from DictReader(file_handler)

    def create_or_update(self, rows):
        for count, row in enumerate(rows, 1):
            create_or_update_reimbursement.delay(row)
            self.print_count(Reimbursement, count=count)

        print('{} reimbursements scheduled to creation/update'.format(count))
