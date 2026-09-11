import sqlite3
from typing import List, Optional, Tuple

class ProductDatabase:
    """SQLite를 사용하여 제품 데이터를 관리하는 클래스"""
    
    def __init__(self, db_name: str = "products.db"):
        """데이터베이스 초기화"""
        self.db_name = db_name
        self.create_table()
    
    def connect(self):
        """데이터베이스 연결"""
        return sqlite3.connect(self.db_name)
    
    def create_table(self):
        """Products 테이블 생성"""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Products (
                productID INTEGER PRIMARY KEY AUTOINCREMENT,
                productName TEXT NOT NULL,
                productPrice INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_product(self, product_name: str, product_price: int) -> int:
        """제품 추가 (입력)
        
        Args:
            product_name: 제품명
            product_price: 제품 가격
        
        Returns:
            추가된 제품의 ID
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO Products (productName, productPrice)
                VALUES (?, ?)
            ''', (product_name, product_price))
            
            conn.commit()
            product_id = cursor.lastrowid
            print(f"✓ 제품이 추가되었습니다. (ID: {product_id}, 제품명: {product_name}, 가격: {product_price})")
            return product_id
        
        except Exception as e:
            print(f"✗ 제품 추가 중 오류가 발생했습니다: {e}")
            return -1
        
        finally:
            conn.close()
    
    def update_product(self, product_id: int, product_name: str = None, product_price: int = None) -> bool:
        """제품 수정
        
        Args:
            product_id: 제품 ID
            product_name: 변경할 제품명 (None이면 변경 안 함)
            product_price: 변경할 가격 (None이면 변경 안 함)
        
        Returns:
            수정 성공 여부
        """
        if product_name is None and product_price is None:
            print("✗ 변경할 항목이 없습니다.")
            return False
        
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            if product_name is not None and product_price is not None:
                cursor.execute('''
                    UPDATE Products
                    SET productName = ?, productPrice = ?
                    WHERE productID = ?
                ''', (product_name, product_price, product_id))
            
            elif product_name is not None:
                cursor.execute('''
                    UPDATE Products
                    SET productName = ?
                    WHERE productID = ?
                ''', (product_name, product_id))
            
            else:  # product_price is not None
                cursor.execute('''
                    UPDATE Products
                    SET productPrice = ?
                    WHERE productID = ?
                ''', (product_price, product_id))
            
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"✓ 제품이 수정되었습니다. (ID: {product_id})")
                return True
            else:
                print(f"✗ ID {product_id}인 제품을 찾을 수 없습니다.")
                return False
        
        except Exception as e:
            print(f"✗ 제품 수정 중 오류가 발생했습니다: {e}")
            return False
        
        finally:
            conn.close()
    
    def delete_product(self, product_id: int) -> bool:
        """제품 삭제
        
        Args:
            product_id: 제품 ID
        
        Returns:
            삭제 성공 여부
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM Products WHERE productID = ?', (product_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                print(f"✓ 제품이 삭제되었습니다. (ID: {product_id})")
                return True
            else:
                print(f"✗ ID {product_id}인 제품을 찾을 수 없습니다.")
                return False
        
        except Exception as e:
            print(f"✗ 제품 삭제 중 오류가 발생했습니다: {e}")
            return False
        
        finally:
            conn.close()
    
    def search_by_id(self, product_id: int) -> Optional[Tuple]:
        """ID로 제품 검색
        
        Args:
            product_id: 제품 ID
        
        Returns:
            (ID, 제품명, 가격) 튜플, 없으면 None
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM Products WHERE productID = ?', (product_id,))
            result = cursor.fetchone()
            
            if result:
                print(f"✓ 검색 결과: ID={result[0]}, 제품명={result[1]}, 가격={result[2]}")
                return result
            else:
                print(f"✗ ID {product_id}인 제품을 찾을 수 없습니다.")
                return None
        
        except Exception as e:
            print(f"✗ 검색 중 오류가 발생했습니다: {e}")
            return None
        
        finally:
            conn.close()
    
    def search_by_name(self, product_name: str) -> List[Tuple]:
        """제품명으로 제품 검색
        
        Args:
            product_name: 제품명 (부분 일치 가능)
        
        Returns:
            검색 결과 리스트
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT * FROM Products WHERE productName LIKE ?',
                (f'%{product_name}%',)
            )
            results = cursor.fetchall()
            
            if results:
                print(f"✓ {len(results)}개의 제품을 찾았습니다:")
                for result in results:
                    print(f"  - ID={result[0]}, 제품명={result[1]}, 가격={result[2]}")
                return results
            else:
                print(f"✗ '{product_name}'을(를) 포함하는 제품을 찾을 수 없습니다.")
                return []
        
        except Exception as e:
            print(f"✗ 검색 중 오류가 발생했습니다: {e}")
            return []
        
        finally:
            conn.close()
    
    def search_by_price_range(self, min_price: int, max_price: int) -> List[Tuple]:
        """가격 범위로 제품 검색
        
        Args:
            min_price: 최소 가격
            max_price: 최대 가격
        
        Returns:
            검색 결과 리스트
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'SELECT * FROM Products WHERE productPrice BETWEEN ? AND ? ORDER BY productPrice',
                (min_price, max_price)
            )
            results = cursor.fetchall()
            
            if results:
                print(f"✓ {len(results)}개의 제품을 찾았습니다 (가격: {min_price}~{max_price}):")
                for result in results:
                    print(f"  - ID={result[0]}, 제품명={result[1]}, 가격={result[2]}")
                return results
            else:
                print(f"✗ 가격 범위 {min_price}~{max_price}에 해당하는 제품이 없습니다.")
                return []
        
        except Exception as e:
            print(f"✗ 검색 중 오류가 발생했습니다: {e}")
            return []
        
        finally:
            conn.close()
    
    def get_all_products(self) -> List[Tuple]:
        """모든 제품 조회
        
        Returns:
            모든 제품의 리스트
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT * FROM Products ORDER BY productID')
            results = cursor.fetchall()
            
            if results:
                print(f"✓ 전체 제품 ({len(results)}개):")
                print("-" * 50)
                print(f"{'ID':<5} {'제품명':<20} {'가격':<10}")
                print("-" * 50)
                for result in results:
                    print(f"{result[0]:<5} {result[1]:<20} {result[2]:<10}")
                print("-" * 50)
                return results
            else:
                print("✗ 등록된 제품이 없습니다.")
                return []
        
        except Exception as e:
            print(f"✗ 조회 중 오류가 발생했습니다: {e}")
            return []
        
        finally:
            conn.close()
    
    def delete_all_products(self) -> bool:
        """모든 제품 삭제 (주의: 되돌릴 수 없음)
        
        Returns:
            삭제 성공 여부
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        try:
            cursor.execute('DELETE FROM Products')
            conn.commit()
            print(f"✓ 모든 제품이 삭제되었습니다.")
            return True
        
        except Exception as e:
            print(f"✗ 삭제 중 오류가 발생했습니다: {e}")
            return False
        
        finally:
            conn.close()


# 사용 예제
if __name__ == "__main__":
    # 데이터베이스 초기화
    db = ProductDatabase("products.db")
    
    print("=" * 50)
    print("제품 관리 시스템 - SQLite CRUD 예제")
    print("=" * 50)
    
    # 1. 제품 추가 (입력)
    print("\n[1] 제품 추가:")
    db.insert_product("노트북", 1500000)
    db.insert_product("마우스", 50000)
    db.insert_product("키보드", 120000)
    db.insert_product("모니터", 300000)
    
    # 2. 모든 제품 조회
    print("\n[2] 모든 제품 조회:")
    db.get_all_products()
    
    # 3. ID로 검색
    print("\n[3] ID로 검색:")
    db.search_by_id(1)
    db.search_by_id(99)
    
    # 4. 제품명으로 검색
    print("\n[4] 제품명으로 검색:")
    db.search_by_name("노")
    db.search_by_name("없는제품")
    
    # 5. 가격 범위로 검색
    print("\n[5] 가격 범위로 검색:")
    db.search_by_price_range(50000, 200000)
    
    # 6. 제품 수정
    print("\n[6] 제품 수정:")
    db.update_product(1, product_price=1800000)
    db.update_product(2, "무선마우스", 65000)
    
    # 7. 수정 후 조회
    print("\n[7] 수정 후 모든 제품 조회:")
    db.get_all_products()
    
    # 8. 제품 삭제
    print("\n[8] 제품 삭제:")
    db.delete_product(4)
    
    # 9. 삭제 후 조회
    print("\n[9] 삭제 후 모든 제품 조회:")
    db.get_all_products()
