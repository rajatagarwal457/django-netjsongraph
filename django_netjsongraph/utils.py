import sys

from datetime import timedelta
from django.utils.timezone import now

from .contextmanagers import log_on_fail
from .models import Topology, Link
from .settings import LINK_EXPIRATION


def print_info(message):  # pragma no cover
    """
    print info message if calling from management command ``update_topology``
    """
    if 'update_topology' in sys.argv:
        print('{0}\n'.format(message))


def delete_expired_links():
    """
    deletes links that have been down for more than
    ``NETJSONGRAPH_LINK_EXPIRATION`` days
    """
    if LINK_EXPIRATION not in [False, None]:
        expiration_date = now() - timedelta(days=int(LINK_EXPIRATION))
        expired_links = Link.objects.filter(status='down',
                                            modified__lt=expiration_date)
        expired_links_length = len(expired_links)
        if expired_links_length:
            print_info('Deleting {0} expired links'.format(expired_links_length))
            for link in expired_links:
                link.delete()


def update_topology(label=None):
    """
    - updates topologies
    - logs failures
    - calls delete_expired_links()
    """
    queryset = Topology.objects.filter(published=True)
    if label:
        queryset = queryset.filter(label__icontains=label)
    for topology in queryset:
        print_info('Updating topology {0}'.format(topology))
        with log_on_fail('update', topology):
            topology.update()
    delete_expired_links()
