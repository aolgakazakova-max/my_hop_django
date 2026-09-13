from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ReviewForm
from .models import Review


@login_required
def review_edit(request, pk):
    review = get_object_or_404(
        Review,
        pk=pk,
        user=request.user,
    )

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)

        if form.is_valid():
            form.save()
            return redirect(
                'products:detail',
                slug=review.product.slug,
            )
    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        'review_edit.html',
        {
            'form': form,
            'review': review,
        },
    )

@login_required
def review_delete(request, pk):
    review = get_object_or_404(
        Review,
        pk=pk,
        user=request.user,
    )

    if request.method == 'POST':
        product_slug = review.product.slug

        review.delete()

        return redirect(
            'products:detail',
            slug=product_slug,
        )

    return render(
        request,
        'review_delete.html',
        {
            'review': review,
        },
    )