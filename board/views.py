from django.shortcuts import render
from django.db import connection
from .models import Board 
from accounts.models import CustomUser
from django.core.paginator import Paginator

def board_home(request):
    content = {'login':'/accounts/login', 'logout':'/accounts/logout', 'register':'/accounts/register', '/accounts':'accounts/'}
    #세션이 존재하면 db에서 값 추출
    if request.session.get('user'):
        user = CustomUser.objects.filter(email = request.session.get('user'))
        print(user.first().name)
        name = user.first().name
        user_dict = {'name':name}
        content = {**content, **user_dict} #딕셔너리 병합
        print(request.session.keys())

    return render(request, 'index.html', content)


def board_list(request):
    cursor = connection.cursor()

    # 검색 키워드와 검색 필드 가져오기
    search_keyword = request.GET.get('search', '').strip()
    search_field = request.GET.get('field', 'title')  # 기본값은 'title'
    page = int(request.GET.get('page', 1))

    # 기본 SQL 쿼리
    sql = 'SELECT b_num, title, email, write_time FROM board WHERE d_check = true'

    # 검색 필드와 키워드에 따라 SQL 조건 추가
    if search_keyword and search_field in ['title', 'content', 'email']:
        sql += f" AND {search_field} LIKE '%%{search_keyword}%%'"

    sql += ' ORDER BY b_num DESC'
    cursor.execute(sql)
    boards = cursor.fetchall()

    # 페이징 처리
    paginator = Paginator(boards, 10)  # 한 페이지에 10개씩 표시
    boards_page = paginator.get_page(page)

    context = {
        'boards': boards_page,
        'search_keyword': search_keyword,
        'search_field': search_field,
        'current_page': boards_page.number,
        'page_range': paginator.get_elided_page_range(page, on_each_side=2, on_ends=1),
        'total_pages': paginator.num_pages,
    }
    return render(request, 'board/list.html', context)


def board_view(request):
    alert=''
    if request.GET.get('b_num'):
        bNum = request.GET.get('b_num')
        
        cursor = connection.cursor()
        sql = f'select title,email,content,v_num,write_time from board where b_num = {bNum} and d_check=true'
        cursor.execute(sql)
        board = cursor.fetchall()
        
        if len(board) != 0:
            # 조회수 로직
            v_num = board[0][3]
            if request.session.get('user') != board[0][1]:
                sql = f'update board set v_num = v_num+1 where b_num = {bNum}'
                cursor.execute(sql)
                v_num += 1
            # 데이터 저장
            content = {
                'title':board[0][0], 
                'email':board[0][1], 
                'content':board[0][2], 
                'v_num':v_num, 
                'write_time':board[0][4],
                'b_num':bNum
                }
        else:
            #글이 존재하지 않을 때
            alert = {'msg':'존재하지 않는 글 입니다.', 'url':'/board/list'}
    else:
        #파라미터 값이 없을 때
        alert = {'msg':'잘못된 접근 입니다.', 'url':'/board'}
    if alert !='': return render(request, 'alert.html', alert)
    return render(request, 'board/view.html', content)

def board_write(request):
    alert=''
    if request.session.get('user'):
        if request.method == "POST":
            #글 작성 로직
            r_title = request.POST.get('title')
            r_content = request.POST.get('content')
            
            if r_title.strip() !='' and r_content.strip() != '':
                Board.objects.create(
                    title = r_title,
                    content = r_content,
                    email = request.session.get('user')
                )   
                alert = {'msg':'글 작성 완료', 'url':'/board/list'}
            else:
                #제목과 내용이 공백일 경우
                alert = {'msg':'제목과 내용을 정확히 입력해 주세요', 'url':'write'}
        else:
            #post로 접근한게 아닐 경우 글 작성 페이지 렌더링
            return render(request, 'board/write.html')
    else:
        #로그인 사용자가 아닐 경우 처리
        alert = {'msg':'로그인 후 작성해 주세요', 'url':'/accounts/login'}

    #로직이 끝난 후 최종 url로 redirect
    return render(request, 'alert.html', alert)

def board_update(request):
    alert=''
    # 수정 view
    if request.GET.get('b_num'):
        bNum = request.GET.get('b_num')
        
        cursor = connection.cursor()
        sql = f'select email,title,content from board where b_num = {bNum} and d_check=true'
        cursor.execute(sql)
        board = cursor.fetchall()
        print(len(board))
        if len(board) != 0:
            if request.session.get('user') == board[0][0]:
                content = {
                    'title':board[0][1],
                    'content':board[0][2],
                    'b_num':bNum
                    }
            else:
                alert = {'msg':'권한이 없습니다.', 'url':'/board/list'}
        else:
            #글이 존재하지 않을 때
            alert = {'msg':'존재하지 않는 글 입니다.', 'url':'/board/list'}
    else:
        #파라미터 값이 없을 때
        alert = {'msg':'잘못된 접근 입니다.', 'url':'/board/list'}
    
    # update요청 처리 로직
    if request.method == "POST":
        bNum = request.POST.get('b_num')
        content = request.POST.get('content')
        print(bNum, content)
        if content.strip() != '':
            cursor = connection.cursor()
            sql = f'update board set content = \'{content}\' where b_num = {bNum}'
            cursor.execute(sql)
            alert = {'msg':'수정 완료', 'url':'/board/view?b_num='+bNum}    
        else:
            alert = {'msg':'수정 실패', 'url':'/board/view?b_num='+bNum}
    if alert !='': return render(request, 'alert.html', alert)
    return render(request, 'board/update.html', content)

def board_delete(request):
    if request.GET.get('b_num'):
        bNum = request.GET.get('b_num')
        cursor = connection.cursor()
        sql = f'select email from board where b_num = {bNum} and d_check=true'
        cursor.execute(sql)
        user = cursor.fetchall()
        if len(user) != 0:
            user = user[0][0]
            if user == request.session.get('user'):
                sql = f'update board set d_check = false where b_num = {bNum}'
                cursor.execute(sql)
                alert = {'msg':'삭제 완료', 'url':'/board/list'}
            else:
                alert = {'msg':'권한이 없습니다.', 'url':'/board/list'}
        else:
            alert = {'msg':'이미 삭제된 글이거나, 존재하지 않습니다.', 'url':'/board/list'}
    else:
        #파라미터 값이 없을 때
        alert = {'msg':'잘못된 접근 입니다.', 'url':'/board/list'}
    return render(request, 'alert.html', alert)
