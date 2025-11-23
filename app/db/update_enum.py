from sqlalchemy import text
from db.base import engine


def update_bp_category_enum():
    """
    Actualiza el enum bp_category en la base de datos para incluir todos los valores necesarios.
    """
    try:
        with engine.connect() as conn:
            # Verificar si el enum existe y tiene los valores correctos
            result = conn.execute(
                text(
                    """
                SELECT enumlabel 
                FROM pg_enum 
                JOIN pg_type ON pg_enum.enumtypid = pg_type.oid 
                WHERE pg_type.typname = 'bp_category'
            """
                )
            )

            existing_values = [row[0] for row in result]
            required_values = ["NORMAL", "ELEVADO", "PREHIPERTENSION", "HIPERTENSION"]

            # Si el enum no existe o no tiene todos los valores, recrearlo
            if set(existing_values) != set(required_values):
                print(
                    f"[INFO] Actualizando enum bp_category. Valores actuales: {existing_values}"
                )

                # Convertir la columna a VARCHAR temporalmente
                conn.execute(
                    text(
                        """
                    ALTER TABLE blood_pressures 
                    ALTER COLUMN category TYPE VARCHAR(50)
                """
                    )
                )
                conn.commit()

                # Eliminar el enum anterior
                conn.execute(text("DROP TYPE IF EXISTS bp_category CASCADE"))
                conn.commit()

                # Crear el nuevo enum
                conn.execute(
                    text(
                        """
                    CREATE TYPE bp_category AS ENUM ('NORMAL', 'ELEVADO', 'PREHIPERTENSION', 'HIPERTENSION')
                """
                    )
                )
                conn.commit()

                # Restaurar la columna con el nuevo enum
                conn.execute(
                    text(
                        """
                    ALTER TABLE blood_pressures 
                    ALTER COLUMN category TYPE bp_category USING category::bp_category
                """
                    )
                )
                conn.commit()

                print("[INFO] Enum bp_category actualizado correctamente")
            else:
                print("[INFO] Enum bp_category ya está actualizado")

    except Exception as e:
        print(f"[ERROR] No se pudo actualizar el enum bp_category: {e}")
        # Si falla, intentar crear el enum desde cero
        try:
            with engine.connect() as conn:
                conn.execute(
                    text(
                        """
                    CREATE TYPE bp_category AS ENUM ('NORMAL', 'ELEVADO', 'PREHIPERTENSION', 'HIPERTENSION')
                """
                    )
                )
                conn.commit()
                print("[INFO] Enum bp_category creado correctamente")
        except Exception as e2:
            print(f"[WARNING] No se pudo crear el enum: {e2}")
