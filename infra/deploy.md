## CosmosDB

### 払い出し

![alt text](image.png)

![alt text](image-1.png)

![alt text](image-2.png)

![alt text](image-3.png)

![alt text](image-3.png)

![alt text](image-4.png)

![alt text](image-5.png)

![alt text](image-6.png)

### Vector機能の有効化
![alt text](image-7.png)

![alt text](image-8.png)

![alt text](image-9.png)

### データベースとコンテナ
vectorフィールドを設定。embedding-largeモデルを使う。
![alt text](image-10.png)


# Outlook API
https://learn.microsoft.com/ja-jp/graph/tutorials/python?context=outlook%2Fcontext&tabs=aad

![alt text](image-14.png)

![alt text](image-15.png)

アプリケーション (クライアント) ID の値をコピー
ディレクトリ (テナント) ID もコピー
- 298002b6-64ce-4554-adcd-412b2eefcb7f
- e4ed36be-38d0-4ddd-9c85-0962719b3135
![alt text](image-16.png)


[ パブリック クライアント フローを許可する] トグルを [はい] に変更
![alt text](image-17.png)

注意事項
- アプリの登録に対して Microsoft Graph のアクセス許可を構成していないことに注意してください。 これは、サンプルで 動的同意 を使用して、ユーザー認証の特定のアクセス許可を要求するためです。

## クライアントシークレット
![alt text](image-25.png)

![alt text](image-26.png)

シークレットの値をコピー
![alt text](image-27.png)

## アクセス権

「アプリケーション許可」のアクセス権を付与
![alt text](image-18.png)

![alt text](image-19.png)

![alt text](image-20.png)

![alt text](image-21.png)

管理者の同意が必要
![alt text](image-22.png)

「エンタープライズアプリケーション」のリンクから同意
![alt text](image-23.png)

![alt text](image-24.png)


## アプリ
requirements.txtに設定
```bash
azure-identity
msgraph-sdk
```

pip install -r requirements.txt