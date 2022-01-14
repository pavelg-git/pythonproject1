import boto3
import uuid


def main():
    s3_resource = boto3.resource('s3',
                                 aws_access_key_id='YOUR_ACCESS_KEY_ID',
                                 aws_secret_access_key='YOUR_SECRET_ACCESS_KEY',
                                 region_name='eu-west-2'
                                 )

    def create_bucket_name(bucket_prefix):
        # The generated bucket name must be between 3 and 63 chars long
        return ''.join([bucket_prefix, str(uuid.uuid4())])

    # YOUR_BUCKET_NAME = create_bucket_name('pavel')
    #
    # bucketname = s3_resource.create_bucket(Bucket=YOUR_BUCKET_NAME,
    #                                        CreateBucketConfiguration={
    #                                            'LocationConstraint': 'eu-west-2'})

    # print(bucketname)

    def create_bucket(bucket_prefix: object, s3_connection: object) -> object:
        session = boto3.session.Session()
        current_region = session.region_name
        bucket_name = create_bucket_name(bucket_prefix)
        bucket_response = s3_connection.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': current_region})
        print(bucket_name, current_region)
        return bucket_name, bucket_response

    first_bucket_name, first_response = create_bucket(
        bucket_prefix='pavelfirstpythonbucket',
        s3_connection=s3_resource.meta.client)
    print(first_response)

    second_bucket_name, second_response = create_bucket(
        bucket_prefix='pavelsecondpythonbucket', s3_connection=s3_resource)
    print(second_response)

    def create_temp_file(size: object, file_name: object, file_content: object) -> object:
        random_file_name = ''.join([str(uuid.uuid4().hex[:6]), file_name])
        with open(random_file_name, 'w') as f:
            f.write(str(file_content) * size)
        return random_file_name

    first_file_name = create_temp_file(300, 'firstfile.txt', 'f')

    first_bucket = s3_resource.Bucket(name=first_bucket_name)

    first_object = s3_resource.Object(
        bucket_name=first_bucket_name, key=first_file_name)
    # print(first_object)
    #
    # first_object_again = first_bucket.Object(first_file_name)
    #
    # first_bucket_again = first_object.Bucket()
    #
    s3_resource.Object(first_bucket_name, first_file_name).upload_file(
        Filename=first_file_name)
    first_object.upload_file(first_file_name)

    # s3_resource.Bucket('firstpythonbucketpaveld75fe6d2-8819-494f-a800-0dbc1486b7d8').upload_file(
    #     Filename=first_file_name, Key=first_file_name)

    # s3_resource.meta.client.upload_file(
    #     Filename=first_file_name, Bucket='firstpythonbucketpaveld75fe6d2-8819-494f-a800-0dbc1486b7d8',
    #     Key=first_file_name)

    s3_resource.Object(first_bucket_name, first_file_name).download_file(
        f'D:/Python/2BDel/{first_file_name}')

    def copy_to_bucket(bucket_from_name, bucket_to_name, file_name):
        copy_source = {
            'Bucket': bucket_from_name,
            'Key': file_name
        }
        s3_resource.Object(bucket_to_name, file_name).copy(copy_source)

    copy_to_bucket(first_bucket_name,
                   second_bucket_name, first_file_name)

    s3_resource.Object(second_bucket_name, first_file_name).delete()

    second_file_name = create_temp_file(400, 'secondfile.txt', 's')
    second_object = s3_resource.Object(first_bucket_name, second_file_name)
    second_object.upload_file(second_file_name, ExtraArgs={
        'ACL': 'public-read'})
    second_object_acl = second_object.Acl()
    second_object_grants = second_object_acl.grants
    print(second_object_grants)

    response = second_object_acl.put(ACL='private')
    second_object_grants = second_object_acl.grants
    print(second_object_grants)

    third_file_name = create_temp_file(300, 'thirdfile.txt', 't')
    third_object = s3_resource.Object(first_bucket_name, third_file_name)
    third_object.upload_file(third_file_name, ExtraArgs={
        'ServerSideEncryption': 'AES256'})
    third_object_encryption = third_object.server_side_encryption
    print(third_object_encryption)

    third_object.upload_file(third_file_name, ExtraArgs={
        'ServerSideEncryption': 'AES256',
        'StorageClass': 'STANDARD_IA'})
    third_object.reload()
    third_object_storage_class = third_object.storage_class
    print(third_object_storage_class)

    def enable_bucket_versioning(bucket_name):
        bkt_versioning = s3_resource.BucketVersioning(bucket_name)
        bkt_versioning.enable()
        print(bkt_versioning.status)

    enable_bucket_versioning(first_bucket_name)

    s3_resource.Object(first_bucket_name, first_file_name).upload_file(
        first_file_name)
    s3_resource.Object(first_bucket_name, first_file_name).upload_file(
        third_file_name)
    s3_resource.Object(first_bucket_name, second_file_name).upload_file(
        second_file_name)

    version = s3_resource.Object(first_bucket_name, first_file_name).version_id
    print(version)

    # for bucket in s3_resource.buckets.all():
    #     print(bucket.name)

    for bucket_dict in s3_resource.meta.client.list_buckets().get('Buckets'):
        print(bucket_dict['Name'])

    for obj in first_bucket.objects.all():
        print(obj.key)

    for obj in first_bucket.objects.all():
        subsrc = obj.Object()
        print(obj.key, obj.storage_class, obj.last_modified,
              subsrc.version_id, subsrc.metadata)

    def delete_all_objects(bucket_name):
        res = []
        bucket = s3_resource.Bucket(bucket_name)
        for obj_version in bucket.object_versions.all():
            res.append({'Key': obj_version.object_key,
                        'VersionId': obj_version.id})
        print(res)
        bucket.delete_objects(Delete={'Objects': res})

    delete_all_objects(first_bucket_name)

    s3_resource.Object(second_bucket_name, first_file_name).upload_file(
        first_file_name)
    delete_all_objects(second_bucket_name)
    s3_resource.Bucket(first_bucket_name).delete()
    s3_resource.meta.client.delete_bucket(Bucket=second_bucket_name)


if __name__ == '__main__':
    main()
