"""
Legacy or placeholder view for rendering a Kanban board template (not used in API).
"""

from django.shortcuts import render


def kanban_board(request):
    """Render the kanban_app/board.html template (for legacy/manual use)."""
    return render(request, 'kanban_app/board.html')
