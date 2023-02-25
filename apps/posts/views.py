from fastapi import Depends, Query, HTTPException, status

from database.db_async import get_async_session
from . import helpers as hls, db_handlers as db_h
from .dependencies import get_user
from .schemas import PostBase, PostAdd, PostUpdate, PostRate, PostSearch


async def add_post(
    post: PostAdd, user=Depends(get_user), session=Depends(get_async_session)
):
    post_db = await db_h.create_post(
        session, user.id, post.title, post.content
    )
    return {
        "detail": "The post was created successfully",
        'data': post_db
    }


async def get_all_posts(
        user=Depends(get_user), session=Depends(get_async_session)
):
    posts = await db_h.get_posts(session)
    return {"status": "Success", "data": posts}


async def get_current_post(
        post_id: int = Query(..., ge=1), user=Depends(get_user),
        session=Depends(get_async_session)
):
    post = await db_h.get_post(session, post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="There is no such post"
        )
    return {"detail": "Success", "data": post}


async def delete_post(
        post_data: PostBase, user=Depends(get_user),
        session=Depends(get_async_session)
):
    await hls.is_post_owner(session, user.id, post_data.id)
    await db_h.delete_post(session, user.id, post_data.id)
    return {"status": "Success", "msg": 'The post was deleted successfully'}


async def change_post(
        post_data: PostUpdate, user=Depends(get_user),
        session=Depends(get_async_session)
):
    await hls.is_post_owner(session, user.id, post_data.id)
    await db_h.change_post(session, user.id, post_data.dict())
    return {"status": "Success", "msg": 'The post was changed successfully'}


async def rate_post(
        post: PostRate, user=Depends(get_user),
        session=Depends(get_async_session)
):
    await hls.is_not_post_owner(session, user.id, post.id)
    await hls.set_rate(
        session, user_id=user.id, post_id=post.id,
        action=post.action.value
    )
    return {"status": "Success",
            "msg": f'You paste {post.action.value} successfully'}


async def unrate_post(
        post: PostBase, user=Depends(get_user),
        session=Depends(get_async_session)
):
    await hls.is_rate_owner(session, user.id, post.id)
    await db_h.delete_rate(session, user.id, post.id)
    return {"status": "Success", "msg": 'The rate was deleted successfully'}


async def search_post(
        post_data: PostSearch, user: dict = Depends(get_user),
        session=Depends(get_async_session)
):
    posts = await db_h.search_posts(
        session, post_data.title, post_data.content
    )
    return {'status': 'Success', 'data': posts}
