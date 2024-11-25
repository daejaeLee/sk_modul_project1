from django.db import models

class Board(models.Model):  
    b_num = models.AutoField(primary_key=True)
    title = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    content = models.TextField()
    write_time = models.DateTimeField(auto_now=True)
    v_num = models.IntegerField(default=0)
    g_num = models.IntegerField(default=0)
    d_check = models.BooleanField(default=True)

    class Meta:
        db_table = 'board'  # 데이터베이스 테이블 이름 설정