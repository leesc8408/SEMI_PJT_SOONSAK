from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Snack
from .models import snack_Category
from reviews.models import Review
from reviews.models import Comment
from carts.forms import CartForm
from .forms import SnackForm, CategoryForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Avg, Count, Q

User = get_user_model()
# 상품 메뉴 전체 조회

# 상품 메뉴 전체 조회
def index(request):
    snacks = Snack.objects.all()
    # 찜 많은순
    snack_like = (
        Snack.objects.all().annotate(like_cnt=Count("likes")).order_by("-like_cnt")[:6]
    )
    # 최신순
    snack_id = Snack.objects.all().order_by("-id")[:6]
    # 리뷰 많은 순
    snack_reviews = (
        Snack.objects.all()
        .prefetch_related("snack_review")
        .annotate(review_cnt=Count("snack_review"))
        .order_by("-review_cnt")[:6]
    )
    # 카테고리
    snack_category = snack_Category.objects.all()
    # 사용자들의 활동지수 
    users = User.objects.all()
    tmp_dict = {}
    for user in users:
        if not user.is_staff:
            score = 0
            score += Review.objects.filter(user__id=user.pk).count()
            score += User.objects.filter(followings=user.pk).count()
            score += Comment.objects.filter(user__id=user.pk).count()
            tmp_dict[user.pk] = score
    user_index_dict = sorted(tmp_dict.items(), key=lambda item: item[1], reverse=True)
    # top3 활동지수 사용자
    if len(user_index_dict) >= 3:
        user_index_dict = sorted(tmp_dict.items(), key=lambda item: item[1], reverse=True)[0:3]
        top1 = User.objects.get(pk=user_index_dict[0][0])
        top2 = User.objects.get(pk=user_index_dict[1][0]) 
        top3 = User.objects.get(pk=user_index_dict[2][0])

        context = {
            "snacks": snacks,
            "snack_id": snack_id,
            "snack_category": snack_category,
            "snack_like": snack_like,
            "snack_reviews": snack_reviews,
            "top1": top1,
            "top2": top2,
            "top3": top3,
        }
        return render(request, "snacks/index.html", context)
    else:

        context = {
            "snacks": snacks,
            "snack_id": snack_id,
            "snack_category": snack_category,
            "snack_like": snack_like,
            "snack_reviews": snack_reviews,
        }
        return render(request, "snacks/index.html", context)
# 상품 카테고리 등록
@login_required(login_url="accounts:login")
def category_create(request):
    # 관리자 권한을 가진 사용자만 상품을 등록할 수 있다.
    if request.user.is_staff:
        if request.method == "POST":
            form = CategoryForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("/")
        else:
            form = CategoryForm()
        context = {
            "form": form,
        }
        return render(request, "snacks/category_create.html", context)
    else:

        return redirect("/")


# 상품 메뉴 등록
@login_required(login_url="accounts:login")
def create(request):
    # 관리자 권한을 가진 사용자만 상품을 등록할 수 있다.
    if request.user.is_staff:
        if request.method == "POST":
            form = SnackForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect("/")
        else:
            form = SnackForm()
        context = {
            "form": form,
        }
        return render(request, "snacks/create.html", context)

    else:
        return redirect("/")


# 상품 메뉴 상세조회
def detail(request, snack_pk):
    snack = get_object_or_404(Snack, pk=snack_pk)
    # 상품 리뷰들
    reviews = Review.objects.filter(snack__pk=snack_pk).order_by("-pk")
    # 장바구니 폼
    form = CartForm()
    # 평균 별점
    try:
        snack_avg = Review.objects.filter(snack__pk=snack_pk).aggregate(Avg("grade"))

        if snack_avg["grade__avg"] > 4.9:
            avg_star = "⭐⭐⭐⭐⭐"
        elif snack_avg["grade__avg"] > 4.4:
            avg_star = "⭐⭐⭐⭐☆"
        elif snack_avg["grade__avg"] > 3.9:
            avg_star = "⭐⭐⭐⭐"
        elif snack_avg["grade__avg"] > 3.4:
            avg_star = "⭐⭐⭐☆"
        elif snack_avg["grade__avg"] > 2.9:
            avg_star = "⭐⭐⭐"
        elif snack_avg["grade__avg"] > 2.4:
            avg_star = "⭐⭐☆"
        elif snack_avg["grade__avg"] > 1.9:
            avg_star = "⭐⭐"
        elif snack_avg["grade__avg"] > 1.4:
            avg_star = "⭐☆"
        elif snack_avg["grade__avg"] > 0.9:
            avg_star = "⭐"
        elif snack_avg["grade__avg"] > 0.4:
            avg_star = "☆"
        else:
            avg_star = "별점 없음"
        snack_avg = round(snack_avg["grade__avg"], 2)
    except:
        avg_star = ""
        snack_avg = "리뷰 없음"
    # 장바구니 폼
    form = CartForm()
    context = {
        "snack": snack,
        "reviews": reviews,
        "form": form,
        "snack_avg": snack_avg,
        "avg_star": avg_star,
    }
    return render(request, "snacks/detail.html", context)


# 상품 수정
@login_required(login_url="accounts:login")
def update(request, snack_pk):
    snack = get_object_or_404(Snack, pk=snack_pk)
    # 관리자 권한을 가진 사용자만 상품을 수정할 수 있다.
    if request.user.is_staff:
        if request.method == "POST":
            form = SnackForm(request.POST, request.FILES, instance=snack)
            if form.is_valid():
                form.save()
                return redirect("snacks:index")
        else:
            form = SnackForm(instance=snack)
        context = {
            "form": form,
        }
        return render(request, "snacks/update.html", context)
    # 관리자가 아니라면 권한 오류 메시지
    else:
        return redirect("/")


# 상품 삭제
def delete(request, snack_pk):
    if request.user.is_staff:
        snack = get_object_or_404(Snack, pk=snack_pk)
        snack.delete()
        return redirect("snacks:index")
    else:
        return redirect("/")


# 상품 좋아요
def likes(request, snack_pk):
    snack = Snack.objects.get(pk=snack_pk)

    if request.user in snack.likes.all():
        snack.likes.remove(request.user)
        existed_user = False
    else:
        snack.likes.add(request.user)
        existed_user = True
    likeCount = snack.likes.count()

    context = {
        "existed_user": existed_user,
        "likeCount": likeCount,
    }

    return JsonResponse(context)


# 상품 카테고리 검색
def search(request, category):
    query = category
    snack_category = snack_Category.objects.get(category=query)
    snacks = Snack.objects.filter(category_id=snack_category)
    context = {
        "snacks": snacks,
    }
    return render(request, "snacks/search.html", context)

# 상품 카테고리 검색
def search_kwargs(request):
    if "kw" in request.POST:
        query = request.POST.get("kw")
        snacks = (
            Snack.objects.filter(Q(name__icontains=query) | Q(category__category=query))
            .annotate(like_cnt=Count("likes"))
            .order_by("-like_cnt")
        )
    context = {"snacks": snacks}
    return render(request, "snacks/search.html", context)
